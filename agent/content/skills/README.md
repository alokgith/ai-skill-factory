# Skills

Each skill lives in its own directory named after its registry `id`:

```text
skills/<skill-id>/
  SKILL.md       required
  examples/      optional
  resources/     optional
```

Start from `skills/_template/SKILL.md`, register the skill in `registry/skills.yaml`, and
follow `docs/skill-development-guidelines.md`.

Files starting with `_` (such as `_template/`) are scaffolding, not registered skills.
