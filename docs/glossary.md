# Glossary

**Task** - a small, idempotent, reversible improvement with a predicate (is it needed?), an
action (do it) and a list of files it may touch.

**Task engine** - ranks applicable tasks, executes them one at a time, and commits each
successful one separately.

**Phase (main / finalize)** - `main` tasks add substance; `finalize` tasks (changelog, generated
indexes) summarise what the main tasks produced and run after them.

**Cooldown** - the number of days before a completed task may be selected again.

**Task history** - `.agent/task-history.json`, the record of completed tasks used for cooldowns.

**Dry run** - `--dry-run`: shows candidates and the selection without changing anything.

**Protected path** - a file pattern tasks may never modify (workflows, config, licences).

**Rollback** - discarding a failed task's uncommitted changes so the run can continue.

**Skill** - a folder of instructions that teaches an AI assistant one capability.

**Registry** - `registry/skills.yaml`, the index of all skills.
