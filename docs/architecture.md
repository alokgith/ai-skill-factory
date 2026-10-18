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

## Planned LLM architecture

Phase 2 adds LLM-backed tasks to the **same** task engine. A task is a task whether it is
deterministic or LLM-powered; the engine, safety checks, history and commit manager are shared.

```text
Deterministic tasks ─┐
                     ├─> Unified task engine -> safety -> validate -> commit
LLM tasks ───────────┘
```

Planned agents (each exposed as one or more tasks):

| Agent | Role |
| --- | --- |
| Researcher | Finds gaps and candidate skills worth building |
| Skill architect | Designs a skill's structure and acceptance criteria |
| Skill writer | Produces `SKILL.md` and supporting files under `skills/` |
| Critic | Reviews drafts against the guidelines and rejects weak output |
| Maintenance agent | Keeps published skills current |

LLM output passes the same diff limits, secret scanning and test gates as every other change.
The `future_llm.enabled` flag stays `false` until this layer exists.
