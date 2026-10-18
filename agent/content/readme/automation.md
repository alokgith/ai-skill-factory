## Automation

`.github/workflows/daily-maintenance.yml` runs at 20:30 UTC (02:00 IST) every day and can be
triggered manually from the Actions tab (optionally as a dry run). It uses the built-in
`GITHUB_TOKEN` with `contents: write` only; no personal token and no LLM key are needed.

```bash
python scripts/run_daily_maintenance.py --dry-run   # preview, changes nothing
python scripts/run_daily_maintenance.py             # real run (commits locally, never pushes)
```

See [docs/automation.md](docs/automation.md) for details.
