import subprocess
from dataclasses import replace
from pathlib import Path

from agent.commit_manager import CommitManager, scan_secrets
from agent.config import Config


def init_repo(root: Path) -> None:
    for args in (["init", "-q"], ["config", "user.name", "Test"],
                 ["config", "user.email", "test@example.invalid"],
                 ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / "keep.txt").write_text("keep\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=root, check=True,
                   capture_output=True)


def manager(root: Path, **overrides) -> CommitManager:
    init_repo(root)
    return CommitManager(root, replace(Config(), **overrides))


def test_clean_tree_detection(tmp_path):
    cm = manager(tmp_path)
    assert cm.is_clean()
    (tmp_path / "new.txt").write_text("x\n", encoding="utf-8")
    assert not cm.is_clean()
    assert cm.changed_files() == ["new.txt"]


def test_expected_change_passes_safety(tmp_path):
    cm = manager(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("# A\n", encoding="utf-8")
    report = cm.check_safety(["docs/*.md"])
    assert report.ok and report.lines_added == 1


def test_unexpected_file_is_flagged(tmp_path):
    cm = manager(tmp_path)
    (tmp_path / "other.txt").write_text("x\n", encoding="utf-8")
    report = cm.check_safety(["docs/*.md"])
    assert not report.ok and "unexpected file changed: other.txt" in report.reasons


def test_too_many_files_is_flagged(tmp_path):
    cm = manager(tmp_path, max_changed_files_per_task=2)
    for i in range(3):
        (tmp_path / f"f{i}.txt").write_text("x\n", encoding="utf-8")
    assert any("files changed" in r for r in cm.check_safety(["f*.txt"]).reasons)


def test_too_many_lines_is_flagged(tmp_path):
    cm = manager(tmp_path, max_lines_added_per_task=5)
    (tmp_path / "big.txt").write_text("line\n" * 6, encoding="utf-8")
    assert any("lines added" in r for r in cm.check_safety(["big.txt"]).reasons)


def test_deletion_is_flagged(tmp_path):
    cm = manager(tmp_path)
    (tmp_path / "keep.txt").unlink()
    assert any("destructive change" in r for r in cm.check_safety(["keep.txt"]).reasons)


def test_protected_path_is_flagged(tmp_path):
    cm = manager(tmp_path)
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "x.yml").write_text("on: push\n", encoding="utf-8")
    reasons = cm.check_safety([".github/workflows/*"]).reasons
    assert any("protected path modified" in r for r in reasons)


def test_extra_allowed_path_is_not_counted(tmp_path):
    cm = manager(tmp_path, max_changed_files_per_task=1)
    (tmp_path / "a.txt").write_text("x\n", encoding="utf-8")
    (tmp_path / "history.json").write_text("{}\n", encoding="utf-8")
    assert cm.check_safety(["a.txt"], extra_allowed=["history.json"]).ok


def test_secret_detection_flags_added_secrets(tmp_path):
    cm = manager(tmp_path)
    fake_key = "AKIA" + "ABCDEFGHIJKLMNOP"  # assembled so this file holds no literal secret
    (tmp_path / "leak.txt").write_text(f"key = {fake_key}\n", encoding="utf-8")
    assert any("possible secret" in r for r in cm.check_safety(["leak.txt"]).reasons)


def test_scan_secrets_ignores_ordinary_text():
    assert scan_secrets("just documentation about tokens and passwords") == []


def test_commit_returns_sha_and_cleans_tree(tmp_path):
    cm = manager(tmp_path)
    (tmp_path / "a.txt").write_text("x\n", encoding="utf-8")
    sha = cm.commit_all("docs: add a\n\nTask: add_a\nRun-Date: 2026-10-19\n")
    assert len(sha) == 7 and cm.is_clean()
    assert cm.find_commit("add_a", "2026-10-19") == sha
    assert cm.find_commit("add_a", "2026-10-20") is None


def test_rollback_restores_a_clean_tree(tmp_path):
    cm = manager(tmp_path)
    (tmp_path / "keep.txt").write_text("changed\n", encoding="utf-8")
    (tmp_path / "new.txt").write_text("x\n", encoding="utf-8")
    cm.stage_all()
    cm.rollback()
    assert cm.is_clean()
    assert (tmp_path / "keep.txt").read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "new.txt").exists()


def test_validate_changes_catches_syntax_yaml_and_json_errors(tmp_path):
    from agent.commit_manager import validate_changes

    (tmp_path / "bad.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "bad.yaml").write_text("a: [1, 2\n", encoding="utf-8")
    (tmp_path / "bad.json").write_text("{nope", encoding="utf-8")
    (tmp_path / "good.md").write_text("# fine\n", encoding="utf-8")
    problems = validate_changes(tmp_path, ["bad.py", "bad.yaml", "bad.json", "good.md"],
                                run_tests=False)
    assert len(problems) == 3
    assert validate_changes(tmp_path, ["good.md"], run_tests=False) == []
