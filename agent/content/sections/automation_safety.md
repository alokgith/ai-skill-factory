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
