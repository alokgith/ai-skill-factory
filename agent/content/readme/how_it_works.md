## How it works

Each daily run follows the same loop:

1. **Inspect** the repository (`agent/repository_inspector.py`) to learn what exists.
2. **Select** applicable tasks from the registry, skipping any completed recently.
3. **Execute** one task, which only writes files.
4. **Check safety**: only expected files changed, diff within limits, no secrets, no deletions.
5. **Validate**: YAML/JSON/Python parse and the test suite passes.
6. **Commit** the task on its own, record it in `.agent/task-history.json`, then repeat.

If any step fails for a task, that task is rolled back and the run continues with the next one.
