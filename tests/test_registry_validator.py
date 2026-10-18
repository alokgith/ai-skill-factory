from pathlib import Path

from agent.registry_validator import validate_registry_data, validate_registry_file

ROOT = Path(__file__).resolve().parents[1]


def skill(**overrides):
    entry = {
        "id": "pdf-summarizer",
        "name": "PDF Summarizer",
        "description": "Summarize PDFs.",
        "status": "draft",
        "path": "skills/pdf-summarizer",
    }
    entry.update(overrides)
    return entry


def messages(data):
    return [str(issue) for issue in validate_registry_data(data)]


def test_empty_registry_is_valid():
    assert validate_registry_data({"skills": []}) == []


def test_well_formed_skill_is_valid():
    assert validate_registry_data({"skills": [skill()]}) == []


def test_shipped_registry_is_valid():
    assert validate_registry_file(ROOT / "registry" / "skills.yaml") == []


def test_duplicate_ids_are_reported():
    found = messages({"skills": [skill(), skill(name="Other")]})
    assert any("duplicate id" in m for m in found)


def test_missing_required_field_is_reported():
    entry = skill()
    del entry["description"]
    assert any("missing required field 'description'" in m for m in messages({"skills": [entry]}))


def test_invalid_status_is_reported():
    assert any("invalid status" in m for m in messages({"skills": [skill(status="live")]}))


def test_non_kebab_case_id_is_reported():
    assert any("invalid id" in m for m in messages({"skills": [skill(id="PDF_Summarizer")]}))


def test_issue_location_identifies_entry():
    found = messages({"skills": [skill(), skill(id="second", status="bad")]})
    assert found == ["skills[1]: invalid status 'bad'"]
