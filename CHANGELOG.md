# Changelog

All notable changes are recorded here, newest first. Entries under Unreleased are added
automatically by the `update_changelog` task, one per completed task.

## [Unreleased]

- docs: add hello-world example skill (`add_example_skill`, 2026-10-21) <!-- task:add_example_skill@2026-10-21 -->
- docs: add skills directory README (`add_skills_readme`, 2026-10-21) <!-- task:add_skills_readme@2026-10-21 -->
- docs: add skill template (`add_skill_template`, 2026-10-21) <!-- task:add_skill_template@2026-10-21 -->
- chore: add Makefile with common commands (`add_makefile`, 2026-10-21) <!-- task:add_makefile@2026-10-21 -->
- chore: add editorconfig (`add_editorconfig`, 2026-10-20) <!-- task:add_editorconfig@2026-10-20 -->
- docs: add security policy (`add_security_policy`, 2026-10-20) <!-- task:add_security_policy@2026-10-20 -->
- chore: add issue template chooser config (`add_issue_template_config`, 2026-10-20) <!-- task:add_issue_template_config@2026-10-20 -->
- chore: add skill proposal issue template (`add_skill_proposal_template`, 2026-10-20) <!-- task:add_skill_proposal_template@2026-10-20 -->
- chore: add feature request issue template (`add_feature_request_template`, 2026-10-20) <!-- task:add_feature_request_template@2026-10-20 -->
- chore: add bug report issue template (`add_bug_report_template`, 2026-10-20) <!-- task:add_bug_report_template@2026-10-20 -->
- chore: add pull request template (`add_pr_template`, 2026-10-19) <!-- task:add_pr_template@2026-10-19 -->
- docs: add project glossary (`add_glossary`, 2026-10-19) <!-- task:add_glossary@2026-10-19 -->
- docs: add commit message conventions (`add_commit_conventions`, 2026-10-19) <!-- task:add_commit_conventions@2026-10-19 -->
- docs: add future LLM integration design (`add_llm_integration_design`, 2026-10-18) <!-- task:add_llm_integration_design@2026-10-18 -->
- docs: add GitHub setup guide (`add_github_setup_guide`, 2026-10-18) <!-- task:add_github_setup_guide@2026-10-18 -->
- docs: add task authoring guide (`add_task_authoring_guide`, 2026-10-18) <!-- task:add_task_authoring_guide@2026-10-18 -->
- docs: document the skill registry schema (`add_registry_schema_docs`, 2026-10-18) <!-- task:add_registry_schema_docs@2026-10-18 -->
- docs: add skill development guidelines (`add_skill_guidelines`, 2026-10-18) <!-- task:add_skill_guidelines@2026-10-18 -->
- docs: add configuration reference (`add_configuration_docs`, 2026-10-18) <!-- task:add_configuration_docs@2026-10-18 -->
- docs: explain how to add a deterministic task (`improve_contributing_guide`, 2026-10-18) <!-- task:improve_contributing_guide@2026-10-18 -->
- docs: outline roadmap phases beyond Phase 1 (`improve_roadmap_docs`, 2026-10-18) <!-- task:improve_roadmap_docs@2026-10-18 -->
- docs: add manual testing guide to automation docs (`add_automation_manual_testing`, 2026-10-18) <!-- task:add_automation_manual_testing@2026-10-18 -->
- docs: document safety and rollback behaviour (`improve_automation_docs`, 2026-10-18) <!-- task:improve_automation_docs@2026-10-18 -->
- docs: describe planned LLM architecture (`improve_architecture_docs`, 2026-10-18) <!-- task:improve_architecture_docs@2026-10-18 -->
- test: add repository validation script tests (`add_validation_script_tests`, 2026-10-18) <!-- task:add_validation_script_tests@2026-10-18 -->
- test: add malformed registry metadata cases (`add_malformed_metadata_tests`, 2026-10-18) <!-- task:add_malformed_metadata_tests@2026-10-18 -->
- test: add registry validation tests (`add_registry_validator_tests`, 2026-10-18) <!-- task:add_registry_validator_tests@2026-10-18 -->
- test: add commit manager safety tests (`add_commit_manager_tests`, 2026-10-18) <!-- task:add_commit_manager_tests@2026-10-18 -->
- test: add task registry consistency tests (`add_task_registry_tests`, 2026-10-18) <!-- task:add_task_registry_tests@2026-10-18 -->
- test: add task history tests (`add_task_history_tests`, 2026-10-18) <!-- task:add_task_history_tests@2026-10-18 -->
- test: add configuration loading tests (`add_config_tests`, 2026-10-18) <!-- task:add_config_tests@2026-10-18 -->
- docs: add Roadmap section to README (`add_readme_roadmap`, 2026-10-18) <!-- task:add_readme_roadmap@2026-10-18 -->
- docs: add Development section to README (`add_readme_development`, 2026-10-18) <!-- task:add_readme_development@2026-10-18 -->
- docs: add Automation section to README (`add_readme_automation`, 2026-10-18) <!-- task:add_readme_automation@2026-10-18 -->
- docs: add How it works section to README (`add_readme_how_it_works`, 2026-10-18) <!-- task:add_readme_how_it_works@2026-10-18 -->
- feat: add repository validation script (`add_validation`, 2026-10-18) <!-- task:add_validation@2026-10-18 -->
- feat: add skill registry validator (`add_registry_validator`, 2026-10-18) <!-- task:add_registry_validator@2026-10-18 -->

## [0.1.0] - 2026-10-19

### Added
- Deterministic task engine, repository inspector, task history and commit manager.
- Safety checks: diff limits, protected paths, secret scan, rollback.
- Daily GitHub Actions workflow and `--dry-run` mode.
- Initial documentation and skill registry scaffold.
