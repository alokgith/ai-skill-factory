# Contributing

Thanks for helping improve AI Skill Factory.

## Ground rules

- Keep changes small and independently revertible.
- Add or update tests for behaviour changes (`python -m pytest`).
- Never commit secrets or API keys.
- Do not edit `.github/workflows/` without discussing permissions first.
- Automated commits follow `type: summary` (`docs`, `test`, `chore`, `feat`, `refactor`).

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```
