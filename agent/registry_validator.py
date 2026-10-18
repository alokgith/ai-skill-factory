"""Validation for registry/skills.yaml (schema: docs/skill-registry-schema.md)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
VALID_STATUSES = ("draft", "tested", "published", "deprecated")
REQUIRED_FIELDS = ("id", "name", "description", "status", "path")


@dataclass(frozen=True)
class ValidationIssue:
    """One problem found in the registry, with where it was found."""

    location: str
    message: str

    def __str__(self) -> str:
        return f"{self.location}: {self.message}"


def validate_registry_data(data: Any) -> list[ValidationIssue]:
    """Validate already-parsed registry data; returns every issue found."""
    if not isinstance(data, dict):
        return [ValidationIssue("registry", "top-level value must be a mapping")]
    if "skills" not in data:
        return [ValidationIssue("registry", "missing required key 'skills'")]
    skills = data["skills"]
    if not isinstance(skills, list):
        return [ValidationIssue("registry", "'skills' must be a list")]

    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    for index, skill in enumerate(skills):
        where = f"skills[{index}]"
        if not isinstance(skill, dict):
            issues.append(ValidationIssue(where, "entry must be a mapping"))
            continue
        for field in REQUIRED_FIELDS:
            if skill.get(field) in (None, ""):
                issues.append(ValidationIssue(where, f"missing required field '{field}'"))
        skill_id = skill.get("id")
        if skill_id not in (None, ""):
            if not isinstance(skill_id, str):
                issues.append(ValidationIssue(where, "'id' must be a string"))
            elif not ID_PATTERN.match(skill_id):
                issues.append(ValidationIssue(where, f"invalid id {skill_id!r}; use kebab-case"))
            elif skill_id in seen_ids:
                issues.append(ValidationIssue(where, f"duplicate id {skill_id!r}"))
            else:
                seen_ids.add(skill_id)
        status = skill.get("status")
        if status not in (None, "") and status not in VALID_STATUSES:
            issues.append(ValidationIssue(where, f"invalid status {status!r}"))
    return issues


def validate_registry_file(path: Path | str) -> list[ValidationIssue]:
    """Load and validate a registry YAML file."""
    p = Path(path)
    if not p.exists():
        return [ValidationIssue(str(p), "file not found")]
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [ValidationIssue(str(p), f"invalid YAML: {exc}")]
    return validate_registry_data(data)
