from pathlib import Path

import pytest

from agent.config import Config, ConfigError, config_from_dict, load_config

ROOT = Path(__file__).resolve().parents[1]


def test_defaults_match_the_documented_values():
    config = Config()
    assert (config.min_commits, config.max_commits) == (3, 8)
    assert config.avoid_recent_days == 7 and not config.future_llm_enabled


def test_missing_file_returns_defaults(tmp_path):
    assert load_config(tmp_path / "nope.yaml") == Config()


def test_shipped_config_loads():
    config = load_config(ROOT / "config" / "config.yaml")
    assert config.enabled and config.min_commits <= config.max_commits
    assert ".github/workflows/*" in config.protected_paths


def test_overrides_are_applied():
    config = config_from_dict({"daily_automation": {"min_commits": 1, "max_commits": 2},
                               "safety": {"max_lines_added_per_task": 50}})
    assert (config.min_commits, config.max_commits, config.max_lines_added_per_task) == (1, 2, 50)


def test_min_greater_than_max_is_rejected():
    with pytest.raises(ConfigError):
        config_from_dict({"daily_automation": {"min_commits": 9, "max_commits": 8}})


def test_future_llm_cannot_be_enabled_in_phase_one():
    with pytest.raises(ConfigError):
        config_from_dict({"future_llm": {"enabled": True}})


def test_wrong_types_are_rejected():
    with pytest.raises(ConfigError):
        config_from_dict({"daily_automation": {"max_commits": "eight"}})
    with pytest.raises(ConfigError):
        config_from_dict({"daily_automation": {"enabled": "yes"}})
    with pytest.raises(ConfigError):
        config_from_dict({"daily_automation": {"max_commits": True}})


def test_invalid_yaml_is_rejected(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("daily_automation: [unclosed\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
