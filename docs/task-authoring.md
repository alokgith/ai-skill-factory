# Task authoring guide

Tasks are declared in `agent/task_registry.py` as `Task` objects.

## The contract

| Field | Requirement |
| --- | --- |
| `name` | Unique snake_case identifier |
| `commit_type` | One of `docs`, `test`, `chore`, `feat`, `refactor` |
| `summary` | Imperative, under ~60 characters; becomes the commit subject |
| `is_applicable(ctx)` | True only while the improvement is still missing |
| `execute(ctx)` | Writes files; never runs git; never overwrites existing work |
| `expected_paths` | Glob patterns for the only files the task may change |
| `phase` | `main` (default) or `finalize` |
| `priority` | Lower runs earlier among applicable tasks |
| `cooldown_days` | Overrides `tasks.avoid_recent_days` |

## Principles

1. **Idempotent.** Once applied, `is_applicable` must return false.
2. **Real value.** Never add content only to create a commit; no timestamp churn.
3. **Small.** One idea per task; under the configured file and line limits.
4. **Additive.** Create files or append sections; do not rewrite or delete.
5. **Testable.** If the task adds code, add (or schedule) tests.

## Checklist

- [ ] `python -m pytest` passes (the registry tests check names, types and templates)
- [ ] `python scripts/run_daily_maintenance.py --dry-run` lists the task when expected
- [ ] The task does not appear once its change exists
