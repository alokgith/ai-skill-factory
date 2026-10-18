from agent.registry_validator import validate_registry_data, validate_registry_file


def first_message(data):
    issues = validate_registry_data(data)
    assert issues, "expected at least one issue"
    return str(issues[0])


def test_top_level_must_be_mapping():
    assert "must be a mapping" in first_message(["not", "a", "mapping"])


def test_none_data_is_rejected():
    assert "must be a mapping" in first_message(None)


def test_missing_skills_key_is_reported():
    assert "missing required key 'skills'" in first_message({"other": 1})


def test_skills_must_be_a_list():
    assert "must be a list" in first_message({"skills": {"id": "x"}})


def test_entry_must_be_a_mapping():
    assert "entry must be a mapping" in first_message({"skills": ["just-a-string"]})


def test_non_string_id_is_reported():
    entry = {"id": 42, "name": "n", "description": "d", "status": "draft", "path": "p"}
    assert "'id' must be a string" in first_message({"skills": [entry]})


def test_empty_values_count_as_missing():
    entry = {"id": "a-b", "name": "", "description": "d", "status": "draft", "path": "p"}
    assert "missing required field 'name'" in first_message({"skills": [entry]})


def test_invalid_yaml_file_is_reported(tmp_path):
    path = tmp_path / "skills.yaml"
    path.write_text("skills: [unclosed\n", encoding="utf-8")
    issues = validate_registry_file(path)
    assert len(issues) == 1 and "invalid YAML" in str(issues[0])


def test_empty_file_is_reported(tmp_path):
    path = tmp_path / "skills.yaml"
    path.write_text("", encoding="utf-8")
    assert "must be a mapping" in str(validate_registry_file(path)[0])


def test_missing_file_is_reported(tmp_path):
    assert "file not found" in str(validate_registry_file(tmp_path / "nope.yaml")[0])
