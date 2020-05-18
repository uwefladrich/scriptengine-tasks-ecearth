"""Tests for helpers/file_handling.py"""

import helpers.file_handling as file_handling
import pytest
import yaml



@pytest.mark.parametrize("exp_id, mon_id, expected_result", [
    ("", "", "none/-"),
    ("exp", "", "none/exp-"),
    ("", "mon id", "none/-mon-id"),
    ("exp","mon id", "none/exp-mon-id"),
])

def test_filename(exp_id, mon_id, expected_result):
    path = "none"
    assert file_handling.filename(exp_id, mon_id, path) == expected_result

@pytest.mark.parametrize("list_of_dicts, expected_input", [
    (5, ["", ""]),
    ({"key": "value"}, ["", ""]),
    ({"exp_id": "exp"}, ["exp", ""]),
    ({"mon_id": "mon id"}, ["", "mon id"]),
    ({"exp_id": "exp","mon_id": "mon id"}, ["exp","mon id"]),
])

def test_convert_to_yaml(tmpdir, list_of_dicts, expected_input):
    file_handling.convert_to_yaml(list_of_dicts, str(tmpdir))
    with open(f"{file_handling.filename(*expected_input,str(tmpdir))}.yml") as file:
        assert list_of_dicts == yaml.load(file, Loader=yaml.FullLoader)