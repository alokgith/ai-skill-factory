from pathlib import Path

from agent.repository_inspector import (
    extract_headings,
    inspect_repository,
    normalize_heading,
)


def make_repo(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_normalize_heading_strips_markers_and_punctuation():
    assert normalize_heading("## What is this?") == "what is this"
    assert normalize_heading("###   How   it works:  ") == "how it works"


def test_extract_headings_ignores_code_fences():
    text = "# Title\n\n```bash\n# not a heading\n```\n\n## Real Section\n"
    assert extract_headings(text) == frozenset({"title", "real section"})


def test_empty_repository_has_no_facts(tmp_path):
    facts = inspect_repository(tmp_path)
    assert not facts.has_readme
    assert not facts.has_tests
    assert not facts.has_docs
    assert not facts.has_registry
    assert facts.untested_modules == ()


def test_detects_documents_templates_and_registry(tmp_path):
    make_repo(tmp_path, {
        "README.md": "# Hi\n",
        "docs/architecture.md": "# Arch\n",
        "docs/configuration.md": "# Config\n",
        "CHANGELOG.md": "# Changelog\n",
        "CONTRIBUTING.md": "# Contributing\n",
        ".github/ISSUE_TEMPLATE/bug_report.md": "x",
        ".github/pull_request_template.md": "x",
        "skills/.gitkeep": "",
        "registry/skills.yaml": "skills: []\n",
        "tests/test_something.py": "def test_x():\n    pass\n",
    })
    facts = inspect_repository(tmp_path)
    assert facts.has_readme and facts.has_docs and facts.has_tests
    assert facts.has_architecture_docs and facts.has_changelog
    assert facts.has_contributing_guide and facts.has_issue_templates
    assert facts.has_pr_template and facts.config_documented
    assert facts.has_skills_dir and facts.has_registry


def test_untested_modules_lists_only_modules_without_tests(tmp_path):
    make_repo(tmp_path, {
        "agent/__init__.py": "",
        "agent/alpha.py": "",
        "agent/beta.py": "",
        "tests/test_alpha.py": "",
    })
    assert inspect_repository(tmp_path).untested_modules == ("agent/beta.py",)


def test_has_heading_reads_file_content(tmp_path):
    make_repo(tmp_path, {"README.md": "# T\n\n## How it works\n"})
    facts = inspect_repository(tmp_path)
    assert facts.has_heading("README.md", "How it works")
    assert not facts.has_heading("README.md", "Roadmap")
    assert not facts.has_heading("MISSING.md", "Anything")


def test_ignored_directories_are_skipped(tmp_path):
    make_repo(tmp_path, {".git/config": "x", "__pycache__/a.pyc": "x", "real.txt": "x"})
    assert inspect_repository(tmp_path).files == frozenset({"real.txt"})
