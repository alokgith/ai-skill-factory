# Security policy

## Reporting a vulnerability

Please report security issues privately using GitHub's *Report a vulnerability* button on the
Security tab. Do not open a public issue for suspected vulnerabilities.

## What the automation can and cannot do

- It uses only the repository's built-in `GITHUB_TOKEN` with `contents: write`.
- It never modifies workflows, protected paths or `config/config.yaml`.
- It refuses changes that delete files, add binaries, or contain apparent secrets.
- It does not call any external service in Phase 1.

## Never commit

API keys, tokens, private keys or credentials. If one is committed by mistake, revoke it
immediately; removing it from history is not enough.
