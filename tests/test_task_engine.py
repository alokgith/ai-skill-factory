import subprocess
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from agent.config import Config
from agent.task_engine import EngineError, TaskEngine
from agent.task_history import TaskHistory
from agent.task_registry import Task

TODAY = date(2026, 10, 19)


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return proc.stdout


def init_repo(root: Path) -> Path:
    git(root, "init", "-q")
    git(root, "config", "user.name", "Test Bot")
    git(root, "config", "user.email", "bot@example.invalid")
    git(root, "config", "commit.gpgsign", "false")
    (root / "README.md").write_text("# Test\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "initial")
    return root


def file_task(name, rel, text="hello\n", *, phase="main", priority=50, expected=None):
    def applicable(ctx):
        return not (ctx.root / rel).exists()

    def execute(ctx):
        path = ctx.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    return Task(name, "docs", f"add {rel}", f"Adds {rel}.", (expected or rel,),
                applicable, execute, phase=phase, priority=priority)


def no_validation(root, changed, full=False):
    return []


def make_engine(root, tasks, config=None, **kwargs):
    kwargs.setdefault("validator", no_validation)
    kwargs.setdefault("today", TODAY)
    kwargs.setdefault("log", lambda message: None)
    return TaskEngine(root, config or Config(), tasks, **kwargs)


def commit_count(root: Path) -> int:
    return int(git(root, "rev-list", "--count", "HEAD").strip())


def test_plan_size_is_deterministic_and_within_bounds():
    config = Config(min_commits=3, max_commits=8)
    sizes = set()
    for day in range(1, 29):
        engine = TaskEngine(".", config, [], today=date(2026, 11, day))
        again = TaskEngine(".", config, [], today=date(2026, 11, day))
        assert engine.plan_size() == again.plan_size()
        assert 3 <= engine.plan_size() <= 8
        sizes.add(engine.plan_size())
    assert len(sizes) >= 4  # the target genuinely varies from day to day


def test_each_task_gets_its_own_commit_and_history_entry(tmp_path):
    init_repo(tmp_path)
    tasks = [file_task(f"t{i}", f"docs/f{i}.md", priority=i) for i in range(4)]
    result = make_engine(tmp_path, tasks, target_override=4).run()
    assert [c.task for c in result.committed] == ["t0", "t1", "t2", "t3"]
    assert commit_count(tmp_path) == 5
    assert git(tmp_path, "status", "--porcelain") == ""
    history = TaskHistory.load(tmp_path / ".agent" / "task-history.json")
    assert [e.task for e in history.entries] == ["t0", "t1", "t2", "t3"]
    assert history.entries[0].commit == result.committed[0].sha  # backfilled by next commit
    body = git(tmp_path, "log", "-1", "--format=%B")
    assert "Task: t3" in body and "Run-Date: 2026-10-19" in body


def test_failing_task_is_rolled_back_and_run_continues(tmp_path):
    init_repo(tmp_path)

    def boom(ctx):
        (ctx.root / "partial.txt").write_text("half done", encoding="utf-8")
        raise RuntimeError("kaput")

    bad = Task("bad", "docs", "bad", "bad", ("partial.txt",), lambda ctx: True, boom, priority=1)
    good = file_task("good", "docs/good.md", priority=2)
    result = make_engine(tmp_path, [bad, good], target_override=2).run()
    assert [c.task for c in result.committed] == ["good"]
    assert result.failed[0][0] == "bad" and "kaput" in result.failed[0][1]
    assert not (tmp_path / "partial.txt").exists()
    assert git(tmp_path, "status", "--porcelain") == ""


def test_oversized_change_is_rejected(tmp_path):
    init_repo(tmp_path)

    def many(ctx):
        for i in range(7):
            (ctx.root / f"f{i}.txt").write_text("x\n", encoding="utf-8")

    task = Task("many", "chore", "many", "many", ("f*.txt",), lambda ctx: True, many)
    result = make_engine(tmp_path, [task], target_override=1).run()
    assert result.committed == []
    assert "files changed" in result.failed[0][1]
    assert not list(tmp_path.glob("f*.txt"))


def test_unexpected_file_is_rejected(tmp_path):
    init_repo(tmp_path)

    def sneaky(ctx):
        (ctx.root / "docs").mkdir()
        (ctx.root / "docs/ok.md").write_text("ok\n", encoding="utf-8")
        (ctx.root / "surprise.txt").write_text("nope\n", encoding="utf-8")

    task = Task("sneaky", "docs", "s", "s", ("docs/ok.md",), lambda ctx: True, sneaky)
    result = make_engine(tmp_path, [task], target_override=1).run()
    assert result.committed == []
    assert "unexpected file changed: surprise.txt" in result.failed[0][1]
    assert not (tmp_path / "docs").exists()


def test_validation_failure_rolls_back(tmp_path):
    init_repo(tmp_path)

    def reject(root, changed, full=False):
        return ["validator says no"] if not full else []

    result = make_engine(tmp_path, [file_task("t", "docs/a.md")],
                         validator=reject, target_override=1).run()
    assert result.committed == []
    assert "validator says no" in result.failed[0][1]
    assert not (tmp_path / "docs/a.md").exists()


def test_noop_task_is_skipped_without_commit(tmp_path):
    init_repo(tmp_path)
    task = Task("noop", "chore", "n", "n", ("x.txt",), lambda ctx: True, lambda ctx: None)
    result = make_engine(tmp_path, [task], target_override=1).run()
    assert result.committed == [] and result.skipped[0][0] == "noop"
    assert commit_count(tmp_path) == 1


def test_recently_completed_tasks_are_not_selected(tmp_path):
    init_repo(tmp_path)
    task = file_task("t", "docs/a.md")
    engine = make_engine(tmp_path, [task])
    engine.history.record("t", "2026-10-15")  # 4 days ago, inside the 7-day window
    assert engine.candidates(engine._context()) == []
    engine.today = date(2026, 10, 25)  # 10 days later -> eligible again
    assert [t.name for t in engine.candidates(engine._context())] == ["t"]


def test_dry_run_preview_changes_nothing(tmp_path):
    init_repo(tmp_path)
    tasks = [file_task("a", "docs/a.md"), file_task("b", "docs/b.md")]
    engine = make_engine(tmp_path, tasks, target_override=2)
    preview = engine.preview()
    assert [t.name for t in preview.selected] == ["a", "b"] or len(preview.selected) == 2
    assert git(tmp_path, "status", "--porcelain") == ""
    assert commit_count(tmp_path) == 1


def test_dirty_working_tree_is_refused(tmp_path):
    init_repo(tmp_path)
    (tmp_path / "scratch.txt").write_text("user work\n", encoding="utf-8")
    with pytest.raises(EngineError):
        make_engine(tmp_path, [file_task("t", "docs/a.md")]).run()
    assert (tmp_path / "scratch.txt").exists()  # never destroyed


def test_pending_history_shas_are_resolved_on_next_run(tmp_path):
    init_repo(tmp_path)
    tasks = [file_task("a", "docs/a.md", priority=1), file_task("b", "docs/b.md", priority=2)]
    first = make_engine(tmp_path, tasks, target_override=2).run()
    later = make_engine(tmp_path, tasks, today=date(2026, 10, 20))
    assert later.history.entries[-1].commit is None  # last sha is not yet on disk
    later._backfill_history()
    assert later.history.entries[-1].commit == first.committed[-1].sha


def test_disabled_automation_does_nothing(tmp_path):
    init_repo(tmp_path)
    config = replace(Config(), enabled=False)
    result = make_engine(tmp_path, [file_task("t", "docs/a.md")], config=config).run()
    assert result.committed == [] and commit_count(tmp_path) == 1


def test_final_validation_failure_is_reported(tmp_path):
    init_repo(tmp_path)

    def fail_full(root, changed, full=False):
        return ["full suite broken"] if full else []

    result = make_engine(tmp_path, [file_task("t", "docs/a.md")],
                         validator=fail_full, target_override=1).run()
    assert not result.ok and result.final_problems == ["full suite broken"]


def test_finalizers_are_reserved_a_slot_when_target_is_large(tmp_path):
    init_repo(tmp_path)
    mains = [file_task(f"m{i}", f"docs/m{i}.md", priority=i) for i in range(6)]
    final = file_task("fin", "docs/index.md", phase="finalize", priority=90)
    result = make_engine(tmp_path, mains + [final], target_override=4).run()
    assert len(result.committed) == 4
    assert "fin" in [c.task for c in result.committed]


def test_never_exceeds_max_commits(tmp_path):
    init_repo(tmp_path)
    tasks = [file_task(f"t{i}", f"docs/t{i}.md", priority=i) for i in range(12)]
    result = make_engine(tmp_path, tasks, target_override=20).run()
    assert len(result.committed) == Config().max_commits


def test_unexpected_validator_crash_rolls_back_instead_of_aborting(tmp_path):
    init_repo(tmp_path)

    def crash(root, changed, full=False):
        raise OSError("disk on fire")

    good = file_task("good", "docs/good.md")
    result = make_engine(tmp_path, [good], validator=crash, target_override=1).run()
    assert result.committed == [] and "disk on fire" in result.failed[0][1]
    assert git(tmp_path, "status", "--porcelain") == ""
