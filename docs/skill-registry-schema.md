# Skill registry schema

`registry/skills.yaml` is the single index of skills. It contains one top-level key, `skills`,
holding a list of entries.

```yaml
skills:
  - id: pdf-summarizer
    name: PDF Summarizer
    description: Summarize long PDF documents into bullet points.
    status: draft
    path: skills/pdf-summarizer
```

## Fields

| Field | Required | Rules |
| --- | --- | --- |
| `id` | yes | Unique, lowercase kebab-case (`a-z`, `0-9`, single hyphens) |
| `name` | yes | Human-readable name |
| `description` | yes | One sentence saying when to use the skill |
| `status` | yes | One of `draft`, `tested`, `published`, `deprecated` |
| `path` | yes | Directory containing the skill's `SKILL.md` |

## Status lifecycle

`draft` -> `tested` -> `published` -> `deprecated`. A skill only moves forward after the
previous stage's checks pass.

## Validation

`agent/registry_validator.py` (added by the automation) reports every violation with its
location, for example `skills[2]: duplicate id 'pdf-summarizer'`.
