## Manual testing

```bash
# Preview the plan; modifies nothing
python scripts/run_daily_maintenance.py --dry-run

# Preview what a particular day would do (selection is seeded by the date)
python scripts/run_daily_maintenance.py --dry-run --date 2026-11-02

# Real run on a clean throw-away clone, forcing exactly three commits
git clone . /tmp/skill-factory-try && cd /tmp/skill-factory-try
git config user.name "Local Test" && git config user.email "test@example.invalid"
python scripts/run_daily_maintenance.py --commits 3
git log --stat -n 3
```

In GitHub, open Actions -> "Daily maintenance" -> "Run workflow" and tick "dry_run" to
preview without committing.
