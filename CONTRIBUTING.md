# Contributing

Thanks for helping improve AI Skill Factory.

## Ground rules

- Keep changes small and independently revertible.
- Add or update tests for behaviour changes (`python -m pytest`).
- Never commit secrets or API keys.
- Do not edit `.github/workflows/` without discussing permissions first.
- Automated commits follow `type: summary` (`docs`, `test`, `chore`, `feat`, `refactor`).

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

## Adding a deterministic task

1. Add a template under `agent/content/` (or write a generator function) for the change.
2. Register a `Task` in `agent/task_registry.py` with:
   - `is_applicable`: true only while the improvement is still missing (idempotent);
   - `execute`: writes files only, never overwrites existing work;
   - `expected_paths`: the exact files it may touch.
3. Keep it small: at most 5 files and 300 added lines by default.
4. Run `python -m pytest` and `python scripts/run_daily_maintenance.py --dry-run`.
