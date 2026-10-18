"""Git operations, safety checks and validation for the task engine.

Every task result passes through ``CommitManager.check_safety`` before it is
committed. Nothing here talks to a network or an LLM.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import yaml

from agent.config import Config

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "provider-style secret key": re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
    "hard-coded credential": re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}['\"]"
    ),
}


class GitError(RuntimeError):
    """Raised when a git command fails."""


@dataclass(frozen=True)
class SafetyReport:
    reasons: tuple[str, ...]
    changed_files: tuple[str, ...]
    lines_added: int

    @property
    def ok(self) -> bool:
        return not self.reasons


def scan_secrets(text: str) -> list[str]:
    """Return the names of secret patterns found in `text`."""
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


class CommitManager:
    """Thin, explicit wrapper around the git CLI."""

    def __init__(self, root: Path | str, config: Config) -> None:
        self.root = Path(root)
        self.config = config

    # ------------------------------------------------------------ plumbing
    def run_git(self, *args: str, check: bool = True) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        if check and proc.returncode != 0:
            detail = proc.stderr.strip() or proc.stdout.strip()
            raise GitError(f"git {' '.join(args)} failed: {detail}")
        return proc.stdout

    def ensure_identity(self) -> None:
        email = self.run_git("config", "--get", "user.email", check=False).strip()
        if not email and not os.environ.get("GIT_AUTHOR_EMAIL"):
            raise GitError(
                "no git identity configured; set user.name/user.email "
                "(the workflow does this automatically)"
            )

    def head_sha(self) -> str:
        return self.run_git("rev-parse", "--short=7", "HEAD").strip()

    # --------------------------------------------------------------- state
    def changed_files(self) -> list[str]:
        out = self.run_git("status", "--porcelain", "-z", "-uall")
        records = [r for r in out.split("\0") if r]
        paths: list[str] = []
        skip_next = False
        for record in records:
            if skip_next:
                skip_next = False
                continue
            status, path = record[:2], record[3:]
            if status[0] in "RC":
                skip_next = True
            paths.append(path)
        return paths

    def is_clean(self) -> bool:
        return not self.changed_files()

    def stage_all(self) -> None:
        self.run_git("add", "-A")

    def _name_status(self) -> list[tuple[str, str]]:
        out = self.run_git("diff", "--cached", "--name-status", "--no-renames", "-z")
        parts = [p for p in out.split("\0") if p]
        return list(zip(parts[0::2], parts[1::2]))

    def _numstat(self) -> list[tuple[str, str, str]]:
        out = self.run_git("diff", "--cached", "--numstat", "--no-renames", "-z")
        rows = []
        for record in (r for r in out.split("\0") if r):
            added, deleted, path = record.split("\t", 2)
            rows.append((added, deleted, path))
        return rows

    def added_text(self) -> str:
        out = self.run_git("diff", "--cached", "-U0", "--no-color", "--no-renames")
        return "\n".join(
            line[1:] for line in out.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )

    # -------------------------------------------------------------- safety
    def check_safety(
        self, expected_paths: Sequence[str], extra_allowed: Sequence[str] = ()
    ) -> SafetyReport:
        """Stage everything and verify the change is small, expected and safe."""
        self.stage_all()
        reasons: list[str] = []
        status = self._name_status()
        paths = [p for _, p in status]
        for code, path in status:
            if code[0] in "DT":
                reasons.append(f"destructive change ({code}) to {path}")
        for path in paths:
            if path in extra_allowed:
                continue
            if _matches(path, self.config.protected_paths):
                reasons.append(f"protected path modified: {path}")
            elif not _matches(path, expected_paths):
                reasons.append(f"unexpected file changed: {path}")
        counted = [p for p in paths if p not in extra_allowed]
        if len(counted) > self.config.max_changed_files_per_task:
            reasons.append(
                f"{len(counted)} files changed (limit {self.config.max_changed_files_per_task})"
            )
        added = 0
        for add, _deleted, path in self._numstat():
            if path in extra_allowed:
                continue
            if add == "-":
                reasons.append(f"binary change not allowed: {path}")
            else:
                added += int(add)
        if added > self.config.max_lines_added_per_task:
            reasons.append(
                f"{added} lines added (limit {self.config.max_lines_added_per_task})"
            )
        for name in scan_secrets(self.added_text()):
            reasons.append(f"possible secret detected: {name}")
        return SafetyReport(tuple(reasons), tuple(paths), added)

    # ------------------------------------------------------------- commits
    def commit_all(self, message: str) -> str:
        self.stage_all()
        self.run_git("commit", "--quiet", "-m", message)
        return self.head_sha()

    def rollback(self) -> None:
        """Discard all uncommitted work. Only call on a tree that started clean."""
        self.run_git("reset", "--hard", "--quiet", "HEAD")
        self.run_git("clean", "-fdq")

    def find_commit(self, task: str, run_date: str) -> str | None:
        """Find the commit carrying the `Task:`/`Run-Date:` trailers."""
        out = self.run_git(
            "log", "-n", "500", "--format=%h%x1f%B%x1e", check=False
        )
        for record in out.split("\x1e"):
            if "\x1f" not in record:
                continue
            sha, body = record.strip().split("\x1f", 1)
            lines = body.splitlines()
            if f"Task: {task}" in lines and f"Run-Date: {run_date}" in lines:
                return sha
        return None


# ------------------------------------------------------------- validation


def validate_changes(
    root: Path | str, changed: Sequence[str], full: bool = False, run_tests: bool = True
) -> list[str]:
    """Check changed files parse, compile, and (where relevant) pass the tests.

    Returns a list of problems; an empty list means everything is fine.
    """
    root_path = Path(root)
    problems: list[str] = []
    for rel in changed:
        path = root_path / rel
        if not path.is_file():
            continue
        try:
            if rel.endswith(".py"):
                compile(path.read_text(encoding="utf-8"), rel, "exec")
            elif rel.endswith((".yaml", ".yml")):
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif rel.endswith(".json"):
                json.loads(path.read_text(encoding="utf-8"))
        except (SyntaxError, ValueError, yaml.YAMLError) as exc:
            problems.append(f"{rel}: {exc}")
    if problems or not run_tests:
        return problems
    needs_tests = full or any(not rel.endswith(".md") for rel in changed)
    if needs_tests:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"],
            cwd=root_path,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-15:])
            problems.append(f"test suite failed:\n{tail}")
    return problems


def make_validator(run_tests: bool):
    """Build the default validator callable used by the engine."""

    def validator(root: Path, changed: Sequence[str], full: bool = False) -> list[str]:
        return validate_changes(root, changed, full=full, run_tests=run_tests)

    return validator
