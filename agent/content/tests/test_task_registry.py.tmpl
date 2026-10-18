import re

from agent.task_registry import (
    CONTENT_DIR,
    COMMIT_TYPES,
    PHASES,
    build_registry,
    render_task_catalog,
)


def test_task_names_are_unique_snake_case():
    names = [t.name for t in build_registry()]
    assert len(names) == len(set(names))
    assert all(re.fullmatch(r"[a-z][a-z0-9_]*", n) for n in names)


def test_tasks_declare_valid_metadata():
    for task in build_registry():
        assert task.commit_type in COMMIT_TYPES
        assert task.phase in PHASES
        assert 10 <= len(task.summary) <= 60, task.name
        assert len(task.commit_subject) <= 72, task.name
        assert task.description.endswith("."), task.name


def test_every_template_exists_and_is_reasonably_small():
    for task in build_registry():
        for template in task.templates:
            path = CONTENT_DIR / template
            assert path.is_file(), f"{task.name}: missing template {template}"
            assert len(path.read_text(encoding="utf-8").splitlines()) <= 150


def test_tasks_never_target_protected_locations():
    for task in build_registry():
        for pattern in task.expected_paths:
            assert not pattern.startswith(".github/workflows"), task.name
            assert not pattern.startswith(".git/"), task.name
            assert pattern != "config/config.yaml", task.name


def test_generated_tasks_are_finalizers_excluded_from_changelog():
    generated = [t for t in build_registry() if t.name.startswith("sync_")]
    assert generated
    for task in generated:
        assert task.phase == "finalize" and not task.changelog


def test_task_catalog_rendering_is_deterministic_and_complete():
    registry = {t.name: t for t in build_registry()}
    first, second = render_task_catalog(registry), render_task_catalog(registry)
    assert first == second
    assert all(f"`{name}`" in first for name in registry)
