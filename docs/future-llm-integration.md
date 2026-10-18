# Future LLM integration

Phase 1 intentionally has no LLM dependency. This note records how the LLM layer is meant to
plug in so the engine does not need rewriting.

## Integration point

LLM-backed tasks are ordinary `Task` objects. Their `execute` function would call an LLM
client, write the result into files, and return. Everything after that - diff limits, secret
scanning, validation, commit, rollback, history - is already shared.

```text
Task(name="draft_skill", execute=call_llm_and_write_files, expected_paths=("skills/*/SKILL.md",))
```

## Required additions (Phase 2)

1. A provider-agnostic client interface in `agent/llm/` with keys read from GitHub secrets.
2. Output validation: schema checks on generated metadata, plus a critic pass before commit.
3. Tighter limits for LLM tasks (cost caps, per-day task counts, prompt/response logging).
4. A `future_llm.enabled` check so LLM tasks are skipped unless explicitly enabled.
5. Evaluation tests that a generated skill meets `docs/skill-development-guidelines.md`.

## Non-goals

LLM output must never bypass the safety checks, modify workflows, or merge its own changes.
