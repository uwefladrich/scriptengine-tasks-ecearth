from helpers.file_handling import filename
import pytest


@pytest.mark.parametrize("dictionary, expected_result", [
    (5, "none/-"),
    ({"key": "value"}, "none/-"),
    ({"exp_id": "exp"}, "none/exp-"),
    ({"mon_id": "mon id"}, "none/-mon-id"),
    ({"exp_id": "exp","mon_id": "mon id"}, "none/exp-mon-id")
])

def test_filename(dictionary, expected_result):
    path = "none"
    assert filename(dictionary,path) == expected_result