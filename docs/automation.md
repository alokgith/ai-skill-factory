# Automation

The workflow in `.github/workflows/daily-maintenance.yml` runs every day at 20:30 UTC
(02:00 IST) and can also be started manually from the Actions tab.

## Steps

1. Check out the repository and install dependencies.
2. Run the test suite; abort if the repository is already broken.
3. Run `scripts/run_daily_maintenance.py`, which selects and executes tasks.
4. Push the resulting commits using the built-in `GITHUB_TOKEN`.

## Task selection

The engine picks a daily target between `min_commits` and `max_commits`, then repeatedly
chooses the highest-priority task that is applicable, not recently completed and not
already attempted. If fewer legitimate tasks exist than the target, it makes fewer commits.

## Commit strategy

Every task becomes its own commit with a conventional subject (`docs: ...`, `test: ...`) and
`Task:` / `Run-Date:` trailers, so any commit can be reverted independently.

## Safety and rollback

Before every commit the engine verifies that:

- only files the task declared in `expected_paths` changed (plus the history file);
- no file was deleted or replaced, and nothing matches `safety.protected_paths`
  (workflows, `.git`, licences, `config/config.yaml`);
- at most `max_changed_files_per_task` files and `max_lines_added_per_task` lines were added;
- no binary files were introduced;
- the added lines contain no private keys, tokens or hard-coded credentials;
- changed YAML/JSON/Python files parse, and the test suite passes where relevant.

If any check fails the task is rolled back with `git reset --hard` and `git clean`, and the
run continues. The run refuses to start on a dirty working tree, so rollback can never
discard unrelated work. Because every task is its own commit, any commit can also be
reverted independently with `git revert`.
