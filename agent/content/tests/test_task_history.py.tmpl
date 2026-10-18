import json
from datetime import date

import pytest

from agent.task_history import HistoryError, TaskHistory


def test_missing_file_gives_empty_history(tmp_path):
    assert TaskHistory.load(tmp_path / "none.json").entries == []


def test_round_trip_preserves_entries(tmp_path):
    path = tmp_path / ".agent" / "history.json"
    history = TaskHistory(path)
    history.record("improve_readme", "2026-10-19", "abc1234")
    history.record("add_test", "2026-10-19")
    history.save()
    loaded = TaskHistory.load(path)
    assert [(e.task, e.date, e.commit) for e in loaded.entries] == [
        ("improve_readme", "2026-10-19", "abc1234"),
        ("add_test", "2026-10-19", None),
    ]
    assert json.loads(path.read_text(encoding="utf-8"))["completed_tasks"][0]["task"] == "improve_readme"


def test_completed_within_respects_the_window(tmp_path):
    history = TaskHistory(tmp_path / "h.json")
    history.record("t", "2026-10-10")
    assert history.completed_within("t", date(2026, 10, 16), 7)       # 6 days ago
    assert not history.completed_within("t", date(2026, 10, 17), 7)   # exactly 7 days ago
    assert not history.completed_within("other", date(2026, 10, 11), 7)


def test_last_completed_returns_latest_date(tmp_path):
    history = TaskHistory(tmp_path / "h.json")
    history.record("t", "2026-10-01")
    history.record("t", "2026-10-05")
    assert history.last_completed("t") == date(2026, 10, 5)
    assert history.last_completed("missing") is None


def test_pending_lists_entries_without_commit(tmp_path):
    history = TaskHistory(tmp_path / "h.json")
    done = history.record("a", "2026-10-19", "abc1234")
    waiting = history.record("b", "2026-10-19")
    assert history.pending() == [waiting] and done not in history.pending()


def test_malformed_history_raises(tmp_path):
    path = tmp_path / "h.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(HistoryError):
        TaskHistory.load(path)
    path.write_text('{"wrong": []}', encoding="utf-8")
    with pytest.raises(HistoryError):
        TaskHistory.load(path)
