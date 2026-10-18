# Configuration reference

All settings live in `config/config.yaml`. Missing keys fall back to safe defaults.

| Key | Default | Meaning |
| --- | --- | --- |
| `daily_automation.enabled` | `true` | Master switch; `false` makes every run a no-op |
| `daily_automation.min_commits` | `3` | Lower bound of the daily commit target |
| `daily_automation.max_commits` | `8` | Upper bound; also a hard cap per run |
| `daily_automation.run_tests` | `true` | Run pytest after each task before committing |
| `tasks.avoid_recent_days` | `7` | Default cooldown before a task can repeat |
| `tasks.history_file` | `.agent/task-history.json` | Where completed tasks are recorded |
| `safety.max_changed_files_per_task` | `5` | Larger changes are rejected and rolled back |
| `safety.max_lines_added_per_task` | `300` | Larger additions are rejected and rolled back |
| `safety.protected_paths` | workflows, `.git`, licences, config | Glob patterns tasks may never modify |
| `future_llm.enabled` | `false` | Reserved for Phase 2; enabling it is rejected today |

## Notes

- The daily target is chosen between `min_commits` and `max_commits` using the date as a seed,
  so a given date always produces the same target. The real count can be lower when fewer
  legitimate tasks apply.
- Some tasks define their own cooldown (for example the changelog task runs at most daily).
- Invalid values (wrong type, `min_commits > max_commits`) stop the run with an error before
  anything is changed.
