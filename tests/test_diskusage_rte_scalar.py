"""Tests for monitoring/diskusage_rte_scalar.py"""

import pytest
import yaml

from monitoring.diskusage_rte_scalar import DiskusageRteScalar, _dir_size

_FILE_SIZE = 10000


@pytest.fixture
def tmp_dir_with_size(tmp_path):
    d = tmp_path / "tmp_dir_with_size"
    d.mkdir()
    f = d / "file_with_size"
    f.write_text(_FILE_SIZE * " ")
    return d


def test_dir_size(tmp_dir_with_size):
    assert _dir_size(tmp_dir_with_size) == _FILE_SIZE


def test_diskusage(tmp_dir_with_size, tmp_path):
    t = DiskusageRteScalar(
        {
            "src": tmp_dir_with_size,
            "dst": tmp_path / "du.yml",
        }
    )
    t.run({})
    with open(tmp_path / "du.yml") as f:
        du = yaml.load(f, Loader=yaml.FullLoader)
    assert du["title"] == "Disk usage in GiB"
    assert du["diagnostic_type"] == "scalar"
    assert du["value"] == round(_FILE_SIZE / 2**30, 1)


def test_not_a_directory(tmp_path, caplog):
    f = tmp_path / "foo"
    f.touch()
    t = DiskusageRteScalar(
        {
            "src": f,
            "dst": tmp_path / "du.yml",
        }
    )
    t.run({})
    with open(tmp_path / "du.yml") as f:
        du = yaml.load(f, Loader=yaml.FullLoader)
    assert du["value"] == 0
    assert " is not a directory" in caplog.text


def test_does_not_exist(tmp_path, caplog):
    t = DiskusageRteScalar(
        {
            "src": "foo",
            "dst": tmp_path / "du.yml",
        }
    )
    t.run({})
    with open(tmp_path / "du.yml") as f:
        du = yaml.load(f, Loader=yaml.FullLoader)
    assert du["value"] == 0
    assert " does not exist" in caplog.text
