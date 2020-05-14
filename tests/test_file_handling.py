from helpers.file_handling import filename
import pytest

def test_filename_no_dict():
    dct = 5
    path = "none"
    with pytest.raises(Exception):
        filename(dct,path)


@pytest.mark.parametrize("dictionary, expected_result", [
    ({"key": "value"}, "none/-"),
    ({"exp_id": "exp"}, "none/exp-"),
    ({"mon_id": "mon id"}, "none/-mon-id"),
    ({"exp_id": "exp","mon_id": "mon id"}, "none/exp-mon-id")
])

def test_filename_dict(dictionary, expected_result):
    path = "none"
    assert filename(dictionary,path) == expected_result