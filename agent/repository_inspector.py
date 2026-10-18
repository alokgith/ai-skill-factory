"""Lightweight, read-only repository inspection used by the task engine."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

IGNORED_DIRS = frozenset(
    {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules",
     ".mypy_cache", ".ruff_cache"}
)
_AGENT_MODULE = re.compile(r"^agent/([A-Za-z0-9_]+)\.py$")


def normalize_heading(text: str) -> str:
    """Lower-case a markdown heading and strip markers/trailing punctuation."""
    cleaned = text.strip().lstrip("#").strip().rstrip(":?.!").strip()
    return re.sub(r"\s+", " ", cleaned).lower()


def extract_headings(markdown: str) -> frozenset[str]:
    """Return normalized headings, ignoring anything inside code fences."""
    headings: set[str] = set()
    in_fence = False
    for line in markdown.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#{1,6}\s+\S", line):
            headings.add(normalize_heading(line))
    return frozenset(headings)


@dataclass(frozen=True)
class RepoFacts:
    """A snapshot of what exists in the repository (relative POSIX paths)."""

    root: Path
    files: frozenset[str]

    def exists(self, rel: str) -> bool:
        return rel in self.files

    def read_text(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def has_heading(self, rel: str, heading: str) -> bool:
        if rel not in self.files:
            return False
        return normalize_heading(heading) in extract_headings(self.read_text(rel))

    @property
    def has_readme(self) -> bool:
        return self.exists("README.md")

    @property
    def has_tests(self) -> bool:
        return any(f.startswith("tests/test_") and f.endswith(".py") for f in self.files)

    @property
    def has_docs(self) -> bool:
        return any(f.startswith("docs/") and f.endswith(".md") for f in self.files)

    @property
    def has_architecture_docs(self) -> bool:
        return self.exists("docs/architecture.md")

    @property
    def has_changelog(self) -> bool:
        return self.exists("CHANGELOG.md")

    @property
    def has_contributing_guide(self) -> bool:
        return self.exists("CONTRIBUTING.md")

    @property
    def has_issue_templates(self) -> bool:
        return any(f.startswith(".github/ISSUE_TEMPLATE/") for f in self.files)

    @property
    def has_pr_template(self) -> bool:
        return self.exists(".github/pull_request_template.md")

    @property
    def config_documented(self) -> bool:
        return self.exists("docs/configuration.md")

    @property
    def has_skills_dir(self) -> bool:
        return any(f.startswith("skills/") for f in self.files)

    @property
    def has_registry(self) -> bool:
        return self.exists("registry/skills.yaml")

    @property
    def untested_modules(self) -> tuple[str, ...]:
        """agent/*.py modules that have no tests/test_<module>.py."""
        missing = []
        for rel in sorted(self.files):
            match = _AGENT_MODULE.match(rel)
            if match and match.group(1) != "__init__":
                if f"tests/test_{match.group(1)}.py" not in self.files:
                    missing.append(rel)
        return tuple(missing)

    def summary(self) -> dict[str, object]:
        """Human-readable facts, used by --dry-run output."""
        return {
            "README exists": self.has_readme,
            "Tests exist": self.has_tests,
            "Documentation exists": self.has_docs,
            "Architecture documentation exists": self.has_architecture_docs,
            "Changelog exists": self.has_changelog,
            "Contributing guide exists": self.has_contributing_guide,
            "GitHub issue templates exist": self.has_issue_templates,
            "GitHub PR template exists": self.has_pr_template,
            "Configuration documented": self.config_documented,
            "Skills directory exists": self.has_skills_dir,
            "Registry exists": self.has_registry,
            "Python modules without tests": list(self.untested_modules),
        }


def inspect_repository(root: Path | str) -> RepoFacts:
    """Walk the repository (skipping VCS/cache dirs) and collect facts."""
    root_path = Path(root).resolve()
    files: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for name in filenames:
            rel = (Path(dirpath) / name).relative_to(root_path)
            files.add(rel.as_posix())
    return RepoFacts(root=root_path, files=frozenset(files))
