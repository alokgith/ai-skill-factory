"""Deterministic task selection and safe execution.

Flow for each run:
    inspect -> rank applicable tasks -> execute one -> safety check -> validate
    -> record history -> commit  (repeat; roll back and move on if anything fails)
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable, Sequence

from agent.commit_manager import CommitManager, make_validator
from agent.config import Config
from agent.repository_inspector import inspect_repository
from agent.task_history import TaskHistory
from agent.task_registry import Task, TaskContext

Validator = Callable[[Path, Sequence[str], bool], list]


class EngineError(RuntimeError):
    """Raised for conditions that make a run unsafe to start."""


@dataclass
class CommittedTask:
    task: str
    subject: str
    sha: str


@dataclass
class RunResult:
    target: int = 0
    committed: list[CommittedTask] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    final_problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.final_problems

    def to_markdown(self) -> str:
        lines = ["## Daily maintenance run", "",
                 f"Target commits: **{self.target}** | made: **{len(self.committed)}** | "
                 f"rolled back: **{len(self.failed)}**", ""]
        lines += [f"- `{c.sha}` {c.subject}" for c in self.committed] or ["- no commits"]
        if self.failed:
            lines += ["", "### Rolled back"] + [f"- `{n}`: {r}" for n, r in self.failed]
        if self.final_problems:
            lines += ["", "### FINAL VALIDATION FAILED"] + [f"- {p}" for p in self.final_problems]
        return "\n".join(lines) + "\n"


@dataclass
class Preview:
    facts: dict
    candidates: list[Task]
    target: int
    selected: list[Task]


class TaskEngine:
    def __init__(
        self,
        root: Path | str,
        config: Config,
        tasks: Sequence[Task],
        *,
        commit_manager: CommitManager | None = None,
        validator: Validator | None = None,
        today: date | None = None,
        seed: str | None = None,
        target_override: int | None = None,
        log: Callable[[str], None] = print,
    ) -> None:
        self.root = Path(root).resolve()
        self.config = config
        self.tasks = list(tasks)
        self.registry = {t.name: t for t in self.tasks}
        if len(self.registry) != len(self.tasks):
            raise EngineError("duplicate task names")
        self.cm = commit_manager or CommitManager(self.root, config)
        self.validator = validator or make_validator(config.run_tests)
        self.today = today or date.today()
        self.seed = seed or self.today.isoformat()
        self.target_override = target_override
        self.log = log
        self.history = TaskHistory.load(self.root / config.history_path)
        self._attempted: set[str] = set()

    # ------------------------------------------------------------ selection
    def plan_size(self) -> int:
        """Deterministic per-day target between min_commits and max_commits."""
        if self.target_override is not None:
            return self.target_override
        rng = random.Random(f"{self.seed}:size")
        return rng.randint(self.config.min_commits, self.config.max_commits)

    def _rank_key(self, task: Task) -> tuple[int, int]:
        digest = hashlib.sha256(f"{self.seed}:{task.name}".encode()).hexdigest()
        return (task.priority, int(digest[:8], 16))

    def _context(self) -> TaskContext:
        return TaskContext(self.root, self.today, inspect_repository(self.root),
                           self.history, self.config, self.registry)

    def _cooling(self, task: Task) -> bool:
        days = task.cooldown_days if task.cooldown_days is not None else self.config.avoid_recent_days
        return self.history.completed_within(task.name, self.today, days)

    def candidates(self, ctx: TaskContext, phase: str | None = None) -> list[Task]:
        """Applicable, not recently completed, not yet attempted; best first."""
        found = []
        for task in self.tasks:
            if phase and task.phase != phase:
                continue
            if task.name in self._attempted or self._cooling(task):
                continue
            try:
                if task.is_applicable(ctx):
                    found.append(task)
            except Exception as exc:  # a broken predicate must never stop the run
                self.log(f"  ! applicability check failed for {task.name}: {exc}")
        return sorted(found, key=self._rank_key)

    def preview(self) -> Preview:
        """Read-only view of what a run would do right now."""
        ctx = self._context()
        main, final = self.candidates(ctx, "main"), self.candidates(ctx, "finalize")
        n = self.plan_size()
        reserve = 1 if n >= 4 else 0
        selected = main[: max(n - reserve, 0)]
        for task in final:
            if len(selected) < n:
                selected.append(task)
        for task in main:
            if len(selected) < n and task not in selected:
                selected.append(task)
        return Preview(ctx.facts.summary(), main + final, n, selected[:n])

    # ------------------------------------------------------------ execution
    def run(self) -> RunResult:
        result = RunResult()
        if not self.config.enabled:
            self.log("Automation disabled in config; nothing to do.")
            return result
        self.cm.ensure_identity()
        if not self.cm.is_clean():
            raise EngineError("working tree is not clean; refusing to run (rollback would be unsafe)")
        self._backfill_history()
        result.target = self.plan_size()
        reserve = 1 if result.target >= 4 else 0
        self.log(f"Target commits for {self.today}: {result.target}")
        self._phase("main", result.target - reserve, result)
        self._phase("finalize", result.target, result)
        self._phase("main", result.target, result)
        if result.committed:
            result.final_problems = self.validator(self.root, [], True)
        return result

    def _phase(self, phase: str, target: int, result: RunResult) -> None:
        budget = self.config.max_commits * 3
        attempts = 0
        while len(result.committed) < min(target, self.config.max_commits) and attempts < budget:
            ranked = self.candidates(self._context(), phase)
            if not ranked:
                return
            task = ranked[0]
            self._attempted.add(task.name)
            attempts += 1
            try:
                self._execute(task, result)
            except Exception as exc:  # last line of defence: never leave a dirty tree
                self._fail(task, f"unexpected error: {exc}", result)

    def _fail(self, task: Task, reason: str, result: RunResult) -> None:
        self.cm.rollback()
        result.failed.append((task.name, reason))
        self.log(f"  x {task.name}: rolled back ({reason.splitlines()[0]})")

    def _execute(self, task: Task, result: RunResult) -> None:
        self.log(f"-> {task.name}")
        try:
            task.execute(self._context())
        except Exception as exc:
            return self._fail(task, f"execution error: {exc}", result)
        if not self.cm.changed_files():
            result.skipped.append((task.name, "no changes produced"))
            self.log(f"  - {task.name}: no changes, skipped")
            return
        try:
            report = self.cm.check_safety(task.expected_paths, (self.config.history_path,))
        except Exception as exc:
            return self._fail(task, f"safety check error: {exc}", result)
        if not report.ok:
            return self._fail(task, "safety: " + "; ".join(report.reasons), result)
        problems = self.validator(self.root, report.changed_files, False)
        if problems:
            return self._fail(task, "validation: " + "; ".join(problems), result)
        entry = self.history.record(task.name, self.today.isoformat(), None)
        try:
            self.history.save()
            sha = self.cm.commit_all(self._message(task))
        except Exception as exc:
            self.history.remove(entry)
            return self._fail(task, f"commit error: {exc}", result)
        entry.commit = sha
        result.committed.append(CommittedTask(task.name, task.commit_subject, sha))
        self.log(f"  + {sha} {task.commit_subject}")

    def _message(self, task: Task) -> str:
        return (
            f"{task.commit_subject}\n\n{task.description}\n\n"
            f"Task: {task.name}\nRun-Date: {self.today.isoformat()}\n"
            "Generated-by: AI Skill Factory task engine (phase 1, no LLM)\n"
        )

    def _backfill_history(self) -> None:
        """Resolve shas for entries whose commit was unknown when written."""
        for entry in self.history.pending():
            sha = self.cm.find_commit(entry.task, entry.date)
            if sha:
                entry.commit = sha
