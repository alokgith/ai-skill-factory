# AI Skill Factory

An autonomous system designed to continuously create, test, publish, and maintain AI skills.

**Current phase (Phase 1):** deterministic autonomous repository maintenance.
**Future phase:** LLM-powered skill research, generation, evaluation, and maintenance.

> The LLM-powered functionality does **not** exist yet. Phase 1 builds and proves the
> autonomous GitHub workflow (scheduling, task selection, validation, commits, rollback)
> that the future LLM agents will run on. No API keys are needed.

## What is this?

A GitHub Actions workflow runs every day, inspects this repository, and makes a handful of
small, reviewable improvements (documentation, tests, templates, validation, generated
indexes), each as its own commit. When there is nothing legitimate left to do, it makes
fewer commits - or none.

## Quick start

```bash
pip install -r requirements.txt
python -m pytest
python scripts/run_daily_maintenance.py --dry-run
```

## How it works

Each daily run follows the same loop:

1. **Inspect** the repository (`agent/repository_inspector.py`) to learn what exists.
2. **Select** applicable tasks from the registry, skipping any completed recently.
3. **Execute** one task, which only writes files.
4. **Check safety**: only expected files changed, diff within limits, no secrets, no deletions.
5. **Validate**: YAML/JSON/Python parse and the test suite passes.
6. **Commit** the task on its own, record it in `.agent/task-history.json`, then repeat.

If any step fails for a task, that task is rolled back and the run continues with the next one.

## Automation

`.github/workflows/daily-maintenance.yml` runs at 20:30 UTC (02:00 IST) every day and can be
triggered manually from the Actions tab (optionally as a dry run). It uses the built-in
`GITHUB_TOKEN` with `contents: write` only; no personal token and no LLM key are needed.

```bash
python scripts/run_daily_maintenance.py --dry-run   # preview, changes nothing
python scripts/run_daily_maintenance.py             # real run (commits locally, never pushes)
```

See [docs/automation.md](docs/automation.md) for details.

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

## Roadmap

- **Phase 1 (now):** deterministic maintenance - tasks, safety, scheduling, history.
- **Phase 2:** LLM-powered researcher, architect, writer and critic agents that add tasks to
  the same engine and populate `registry/skills.yaml`.
- **Phase 3:** automated skill evaluation, publishing and long-term maintenance.

Details: [docs/roadmap.md](docs/roadmap.md).
