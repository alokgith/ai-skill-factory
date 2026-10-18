# GitHub setup

## One-time repository settings

1. **Actions permissions** - Settings -> Actions -> General -> *Workflow permissions*: choose
   **Read and write permissions**. (The workflow also declares `contents: write` itself.)
2. **Allow Actions** - make sure GitHub Actions is enabled for the repository.
3. **Branch protection** - if the default branch requires pull requests or status checks, the
   built-in token cannot push to it. Either allow the Actions bot to bypass the rule, or leave
   the default branch unprotected for this repository.

No secrets are required in Phase 1.

## Optional: commit author

By default commits are authored by `github-actions[bot]`. To use a different identity, add
repository **variables** (Settings -> Secrets and variables -> Actions -> Variables):

- `COMMIT_AUTHOR_NAME`
- `COMMIT_AUTHOR_EMAIL`

Note that GitHub attributes commits to a profile (and its contribution graph) by author email,
so use an address that is verified on the account you intend.

## Running it

- Scheduled: every day at 20:30 UTC (02:00 IST). Scheduled runs can start a few minutes late.
- Manual: Actions -> *Daily maintenance* -> *Run workflow*; tick `dry_run` to preview.

## Troubleshooting

- **Push rejected** - branch protection (see above) or insufficient workflow permissions.
- **Baseline tests fail** - fix the failing test first; the workflow refuses to add commits
  on top of a broken repository.
- **Zero commits** - not an error: it means no applicable tasks were left or all were cooling down.
- **Schedule stopped** - GitHub may pause scheduled workflows in repositories with no recent
  activity; re-enable from the Actions tab.
