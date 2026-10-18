"""Persistent record of completed tasks (.agent/task-history.json)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


class HistoryError(ValueError):
    """Raised when the history file cannot be parsed."""


@dataclass
class HistoryEntry:
    task: str
    date: str
    commit: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"task": self.task, "date": self.date, "commit": self.commit}


class TaskHistory:
    """Ordered list of completed tasks, newest last."""

    def __init__(self, path: Path, entries: list[HistoryEntry] | None = None) -> None:
        self.path = Path(path)
        self.entries: list[HistoryEntry] = entries if entries is not None else []

    @classmethod
    def load(cls, path: Path | str) -> "TaskHistory":
        p = Path(path)
        if not p.exists():
            return cls(p)
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            items = raw["completed_tasks"]
            entries = [
                HistoryEntry(str(i["task"]), str(i["date"]), i.get("commit"))
                for i in items
            ]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise HistoryError(f"malformed task history {p}: {exc}") from exc
        return cls(p, entries)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"completed_tasks": [e.to_dict() for e in self.entries]}
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def record(self, task: str, day: str, commit: str | None = None) -> HistoryEntry:
        entry = HistoryEntry(task, day, commit)
        self.entries.append(entry)
        return entry

    def remove(self, entry: HistoryEntry) -> None:
        self.entries.remove(entry)

    def pending(self) -> list[HistoryEntry]:
        """Entries whose commit sha has not been resolved yet."""
        return [e for e in self.entries if e.commit is None]

    def last_completed(self, task: str) -> date | None:
        days = [date.fromisoformat(e.date) for e in self.entries if e.task == task]
        return max(days) if days else None

    def completed_within(self, task: str, today: date, days: int) -> bool:
        """True if `task` was completed fewer than `days` days before `today`."""
        last = self.last_completed(task)
        return last is not None and (today - last).days < days
