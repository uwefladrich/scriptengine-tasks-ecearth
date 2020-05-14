import sys
sys.path.append(".")

from ..helpers.file_handling import filename
import pytest

def test_filename():
    dct = 5
    path = "none"
    with pytest.raises(Exception):
        filename(dct,path)
    dct = {
        "key": "value"
    }
    assert filename(dct,path) == "none/-"
    dct = {
        "exp_id": "exp",
        }
    assert filename(dct,path) == "none/exp-"
    dct = {
        "mon_id": "mon id",
        }
    assert filename(dct,path) == "none/-mon-id"
    dct = {
        "exp_id": "exp",
        "mon_id": "mon id",
        }
    assert filename(dct,path) == "none/exp-mon-id"