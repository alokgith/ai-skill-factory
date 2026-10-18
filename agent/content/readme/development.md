## Development

Requirements: Python 3.11+, `pyyaml`, `pytest`.

```text
agent/      task engine, registry, inspector, history, commit manager
scripts/    command-line entry points
config/     config.yaml (limits, cooldowns, feature flags)
registry/   skills.yaml (populated by the future LLM agent)
skills/     generated skills will live here
docs/       architecture, automation and guides
tests/      pytest suite
```

Run the tests with `python -m pytest`. To add automation, write a new task in
`agent/task_registry.py` (see CONTRIBUTING.md).
