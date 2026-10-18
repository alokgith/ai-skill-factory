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
