#!/usr/bin/env python3
"""Validate repository health: required files, YAML/JSON syntax and the skill registry.

Usage: python scripts/validate_repository.py
Exit status is 0 when healthy, 1 when problems are found.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from agent.registry_validator import validate_registry_file  # noqa: E402

REQUIRED_FILES = (
    "README.md",
    "config/config.yaml",
    "registry/skills.yaml",
    ".github/workflows/daily-maintenance.yml",
)
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}


def collect_issues(root: Path) -> list[str]:
    """Return a list of human-readable problems; empty means healthy."""
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing required file: {rel}")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            try:
                if name.endswith((".yaml", ".yml")):
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                elif name.endswith(".json"):
                    json.loads(path.read_text(encoding="utf-8"))
            except (yaml.YAMLError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                issues.append(f"{rel}: cannot parse ({type(exc).__name__})")
    registry = root / "registry" / "skills.yaml"
    if registry.exists():
        issues += [f"registry: {issue}" for issue in validate_registry_file(registry)]
    return issues


def main() -> int:
    issues = collect_issues(ROOT)
    for issue in issues:
        print(f"FAIL {issue}")
    print("Repository is healthy." if not issues else f"{len(issues)} problem(s) found.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
