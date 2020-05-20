"""Tests for helpers/file_handling.py"""

import helpers.file_handling as file_handling
import pytest
import yaml



@pytest.mark.parametrize("mon_id, expected_result", [
    ("", "none/"),
    ("mon id", "none/mon-id"),
])

def test_filename(mon_id, expected_result):
    path = "none"
    assert file_handling.filename(mon_id, path) == expected_result

@pytest.mark.parametrize("list_of_dicts, expected_input", [
    (5, ""),
    ({"key": "value"}, ""),
    ({"mon_id": "mon id"}, "mon id"),
])

def test_convert_to_yaml(tmpdir, list_of_dicts, expected_input):
    file_handling.convert_to_yaml(list_of_dicts, str(tmpdir))
    path = file_handling.filename(expected_input,str(tmpdir))
    with open(f"{path}.yml") as file:
        assert list_of_dicts == yaml.load(file, Loader=yaml.FullLoader)