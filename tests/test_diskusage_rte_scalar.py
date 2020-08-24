"""Tests for scriptengine/tasks/ecearth/monitoring/disk_usage.py"""

from unittest.mock import patch

import yaml

from scriptengine.tasks.ecearth.monitoring.diskusage_rte_scalar import DiskusageRteScalar

def test_diskusage_working(tmpdir):
    test_path = str(tmpdir)
    subfile = tmpdir.mkdir("sub").join("file.txt")
    subfile.write("content")
    path = test_path + 'test.yml'
    init = {
        'src': test_path,
        'dst': path,
    }
    context = init
    disk_usage = DiskusageRteScalar(init)
    disk_usage.run(context)
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert result['diagnostic_type'] == disk_usage.diagnostic_type
    assert result['data'] == 0.0 # DiskUsage rounds to GB


def test_not_a_directory(tmpdir):
    path = tmpdir.mkdir("sub").join("hello.yml")
    path.write("content")
    init = {
        'src': str(path),
        'dst': str(path),
    }
    context = init
    disk_usage = DiskusageRteScalar(init)
    disk_usage.run(context)
    expected_result = {
        'title': "Disk Usage in GB",
        'diagnostic_type': disk_usage.diagnostic_type,
        'data': -1,
    }
    with patch.object(disk_usage, 'log_warning') as mock:
        disk_usage.run(context)
    mock.assert_called_with(f"{path} is not a directory. Returning -1.")
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result['title'] == result['title']
    assert expected_result['diagnostic_type'] == result['diagnostic_type']
    assert expected_result['data'] == result['data']

def test_permission_error(tmpdir):
    path = str(tmpdir) + '/test.yml'
    forbidden = '/root'
    init = {
        'src': forbidden,
        'dst': str(path),
    }
    context = init
    disk_usage = DiskusageRteScalar(init)
    disk_usage.run(context)
    expected_result = {
        'title': "Disk Usage in GB",
        'diagnostic_type': disk_usage.diagnostic_type,
        'data': -1,
    }
    with patch.object(disk_usage, 'log_warning') as mock:
        disk_usage.run(context)
    mock.assert_called_with(f"No permission to open {forbidden}. Returning -1.")
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result['title'] == result['title']
    assert expected_result['diagnostic_type'] == result['diagnostic_type']
    assert expected_result['data'] == result['data']