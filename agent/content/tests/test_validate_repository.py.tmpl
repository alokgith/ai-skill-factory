import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script():
    spec = importlib.util.spec_from_file_location(
        "validate_repository", ROOT / "scripts" / "validate_repository.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_this_repository_is_healthy():
    assert load_script().collect_issues(ROOT) == []


def test_missing_required_files_are_reported(tmp_path):
    issues = load_script().collect_issues(tmp_path)
    assert "missing required file: README.md" in issues


def test_broken_yaml_is_reported(tmp_path):
    (tmp_path / "bad.yaml").write_text("a: [1, 2\n", encoding="utf-8")
    issues = load_script().collect_issues(tmp_path)
    assert any(i.startswith("bad.yaml: cannot parse") for i in issues)


def test_broken_json_is_reported(tmp_path):
    (tmp_path / "bad.json").write_text("{nope", encoding="utf-8")
    issues = load_script().collect_issues(tmp_path)
    assert any(i.startswith("bad.json: cannot parse") for i in issues)


def test_invalid_registry_is_reported(tmp_path):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "skills.yaml").write_text("skills: nope\n", encoding="utf-8")
    issues = load_script().collect_issues(tmp_path)
    assert any(i.startswith("registry:") for i in issues)
