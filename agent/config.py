"""Configuration loading and validation for the automation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = "config/config.yaml"


class ConfigError(ValueError):
    """Raised when config/config.yaml is malformed or inconsistent."""


@dataclass(frozen=True)
class Config:
    """Typed view of config/config.yaml. Every field has a safe default."""

    enabled: bool = True
    min_commits: int = 3
    max_commits: int = 8
    run_tests: bool = True
    avoid_recent_days: int = 7
    history_path: str = ".agent/task-history.json"
    max_changed_files_per_task: int = 5
    max_lines_added_per_task: int = 300
    protected_paths: tuple[str, ...] = (
        ".github/workflows/*",
        ".git/*",
        "LICENSE*",
        "config/config.yaml",
    )
    future_llm_enabled: bool = False

    def validate(self) -> None:
        if self.min_commits < 0 or self.max_commits < 1:
            raise ConfigError("min_commits must be >= 0 and max_commits >= 1")
        if self.min_commits > self.max_commits:
            raise ConfigError("min_commits cannot exceed max_commits")
        if self.avoid_recent_days < 0:
            raise ConfigError("avoid_recent_days must be >= 0")
        if self.max_changed_files_per_task < 1 or self.max_lines_added_per_task < 1:
            raise ConfigError("safety limits must be positive")
        if self.future_llm_enabled:
            raise ConfigError(
                "future_llm.enabled must stay false: no LLM layer exists in Phase 1"
            )


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"'{name}' must be a mapping")
    return value


def _typed(section: dict[str, Any], key: str, kind: type, default: Any) -> Any:
    value = section.get(key, default)
    if kind is int and isinstance(value, bool):
        raise ConfigError(f"'{key}' must be an integer")
    if not isinstance(value, kind):
        raise ConfigError(f"'{key}' must be of type {kind.__name__}")
    return value


def config_from_dict(data: dict[str, Any]) -> Config:
    """Build and validate a Config from parsed YAML."""
    d = Config()
    daily = _section(data, "daily_automation")
    tasks = _section(data, "tasks")
    safety = _section(data, "safety")
    llm = _section(data, "future_llm")
    protected = safety.get("protected_paths", list(d.protected_paths))
    if not isinstance(protected, list) or not all(isinstance(p, str) for p in protected):
        raise ConfigError("'protected_paths' must be a list of strings")
    config = Config(
        enabled=_typed(daily, "enabled", bool, d.enabled),
        min_commits=_typed(daily, "min_commits", int, d.min_commits),
        max_commits=_typed(daily, "max_commits", int, d.max_commits),
        run_tests=_typed(daily, "run_tests", bool, d.run_tests),
        avoid_recent_days=_typed(tasks, "avoid_recent_days", int, d.avoid_recent_days),
        history_path=_typed(tasks, "history_file", str, d.history_path),
        max_changed_files_per_task=_typed(
            safety, "max_changed_files_per_task", int, d.max_changed_files_per_task
        ),
        max_lines_added_per_task=_typed(
            safety, "max_lines_added_per_task", int, d.max_lines_added_per_task
        ),
        protected_paths=tuple(protected),
        future_llm_enabled=_typed(llm, "enabled", bool, d.future_llm_enabled),
    )
    config.validate()
    return config


def load_config(path: Path | str) -> Config:
    """Load configuration; a missing file yields the defaults."""
    p = Path(path)
    if not p.exists():
        return Config()
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{p} must contain a mapping at the top level")
    return config_from_dict(data)
