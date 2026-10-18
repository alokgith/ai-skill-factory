#!/usr/bin/env python3
"""Run (or preview) the daily deterministic maintenance.

    python scripts/run_daily_maintenance.py --dry-run
    python scripts/run_daily_maintenance.py

This script never pushes; the GitHub Actions workflow does that afterwards.
"""
from __future__ import annotations

import argparse
import dataclasses
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.config import DEFAULT_CONFIG_PATH, ConfigError, load_config  # noqa: E402
from agent.task_engine import EngineError, TaskEngine  # noqa: E402
from agent.task_history import HistoryError  # noqa: E402
from agent.task_registry import build_registry  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dry-run", action="store_true", help="show the plan; change nothing")
    p.add_argument("--root", default=str(ROOT), help="repository root (default: this repo)")
    p.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="config path relative to root")
    p.add_argument("--date", help="override today's date (YYYY-MM-DD), for testing")
    p.add_argument("--commits", type=int, help="override the daily commit target, for testing")
    p.add_argument("--no-tests", action="store_true", help="skip running pytest per task")
    return p.parse_args(argv)


def print_preview(engine: TaskEngine) -> None:
    preview = engine.preview()
    print("Repository facts:")
    for key, value in preview.facts.items():
        print(f"  {key}: {value}")
    print("\nCandidate tasks:")
    for i, task in enumerate(preview.candidates, 1):
        print(f"{i}. {task.summary}  [{task.name}]")
    if not preview.candidates:
        print("(none - the repository is up to date)")
    print(f"\nTarget commits today: {preview.target}")
    print("\nSelected:")
    for i, task in enumerate(preview.selected, 1):
        print(f"{i}. {task.commit_subject}")
    if not preview.selected:
        print("(nothing selected)")
    print("\nNote: tasks that depend on earlier ones (e.g. README sections) can become")
    print("applicable during a real run, so a live run may select slightly differently.")
    print("\nNo files modified.\nNo commits created.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    try:
        config = load_config(root / args.config)
        if args.no_tests:
            config = dataclasses.replace(config, run_tests=False)
        today = date.fromisoformat(args.date) if args.date else date.today()
        engine = TaskEngine(root, config, build_registry(), today=today,
                            target_override=args.commits)
        if args.dry_run:
            print_preview(engine)
            return 0
        result = engine.run()
    except (ConfigError, HistoryError, EngineError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"\nDone: {len(result.committed)} commit(s), {len(result.failed)} rolled back.")
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write(result.to_markdown())
    if not result.ok:
        print("Final validation FAILED:", *result.final_problems, sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
