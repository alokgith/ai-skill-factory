# Architecture

AI Skill Factory is built in layers so that LLM-powered agents can be added without
rewriting the automation underneath them.

## Components (Phase 1)

| Component | File | Responsibility |
| --- | --- | --- |
| Repository inspector | `agent/repository_inspector.py` | Read-only snapshot of what exists |
| Task registry | `agent/task_registry.py` | Declares tasks: applicability, action, allowed paths |
| Task engine | `agent/task_engine.py` | Ranks tasks, executes, validates, commits, rolls back |
| Commit manager | `agent/commit_manager.py` | Git operations and safety checks |
| Task history | `agent/task_history.py` | `.agent/task-history.json`, prevents repetition |
| Config | `agent/config.py` | Typed view of `config/config.yaml` |

## Data flow

```text
inspect repository -> applicable tasks -> rank -> execute -> safety check
                   -> validate (tests) -> record history -> commit
```

No component calls an LLM or any network service in Phase 1.
