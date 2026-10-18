# Commit conventions

Automated commits use `type: summary` subjects:

| Type | Used for |
| --- | --- |
| `docs` | Documentation, README, changelog, generated indexes |
| `test` | New or improved tests |
| `feat` | New utilities or validation code |
| `chore` | Templates, configuration, tooling |
| `refactor` | Behaviour-preserving code changes |

Each commit also carries trailers:

```text
Task: add_config_tests
Run-Date: 2026-10-19
Generated-by: AI Skill Factory task engine (phase 1, no LLM)
```

`Task` and `Run-Date` let the engine map a history entry back to its commit. Every commit is
independent and can be reverted with `git revert <sha>`.
