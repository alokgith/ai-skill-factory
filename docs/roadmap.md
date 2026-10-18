# Roadmap

## Phase 1: deterministic maintenance (current)

- [x] Task engine, inspector, history, commit manager
- [x] Safety limits and rollback
- [x] Daily scheduled workflow with manual trigger and dry run
- [x] Documentation, templates and validation tasks
- [ ] Observe real daily runs and tune task priorities

## Phase 2 and beyond

### Phase 2: LLM-powered skill generation

- [ ] Add an LLM client behind a provider interface (keys read from GitHub secrets)
- [ ] Researcher and skill-architect tasks that propose skills
- [ ] Skill-writer task that drafts `skills/<id>/SKILL.md`
- [ ] Critic task that gates drafts before they are committed
- [ ] Populate `registry/skills.yaml` and validate it on every change

### Phase 3: evaluation, publishing and maintenance

- [ ] Automated skill evaluation suites
- [ ] Publishing workflow with human approval
- [ ] Maintenance agent that refreshes outdated skills
