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
