# Skill development guidelines

A *skill* is a self-contained folder of instructions (and optional resources) that teaches an
AI assistant how to do one kind of task well. These guidelines apply to humans now and to the
LLM agents added in Phase 2.

## What makes a good skill

- **One job.** Describe a single capability; split broad skills.
- **Clear trigger.** The `description` says when to use the skill, not just what it is.
- **Actionable steps.** Prefer concrete procedures and examples over general advice.
- **Honest limits.** State what the skill cannot do and when to ask a human.
- **No secrets.** Never embed credentials, personal data or private URLs.

## Layout

```text
skills/<skill-id>/
  SKILL.md        required: metadata header and instructions
  examples/       optional worked examples
  resources/      optional reference files
```

`<skill-id>` is lowercase kebab-case and must match the `id` in `registry/skills.yaml`.

## Review checklist

1. Does the description make the trigger obvious?
2. Can someone follow the steps without extra context?
3. Are examples realistic and correct?
4. Is the skill registered and does `scripts/validate_repository.py` pass?
