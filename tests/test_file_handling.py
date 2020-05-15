import helpers.file_handling as file_handling
import pytest
import yaml



@pytest.mark.parametrize("dictionary, expected_result", [
    (5, "none/-"),
    ({"key": "value"}, "none/-"),
    ({"exp_id": "exp"}, "none/exp-"),
    ({"mon_id": "mon id"}, "none/-mon-id"),
    ({"exp_id": "exp","mon_id": "mon id"}, "none/exp-mon-id"),
])

def test_filename(dictionary, expected_result):
    path = "none"
    assert file_handling.filename(dictionary,path) == expected_result

@pytest.mark.parametrize("list_of_dicts", [
    5,
    {"key": "value"},
    {"exp_id": "exp"},
    {"mon_id": "mon id"},
    {"exp_id": "exp","mon_id": "mon id"},
])

def test_convert_to_yaml(tmpdir, list_of_dicts):
    file_handling.convert_to_yaml(list_of_dicts, str(tmpdir))
    with open(f"{file_handling.filename(list_of_dicts,str(tmpdir))}.yml") as file:
        assert list_of_dicts == yaml.load(file, Loader=yaml.FullLoader)