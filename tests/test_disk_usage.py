"""Tests for scriptengine/tasks/ecearth/monitoring/disk_usage.py"""

import os

import pytest
import yaml
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.disk_usage import DiskUsage

def test_disk_usage_working(tmpdir):
    test_path = str(tmpdir)
    subfile = tmpdir.mkdir("sub").join("file.txt")
    subfile.write("content")
    path = test_path + 'test.yml'
    init = {
        'src': test_path,
        'dst': path,
    }
    context = init
    disk_usage = DiskUsage(init)
    disk_usage.run(context)
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert result['title'] == disk_usage.title
    assert result['comment'] == disk_usage.comment
    assert result['type'] == disk_usage.type
    assert result['data'] == 0.0 # DiskUsage rounds to GB


def test_not_a_directory(tmpdir):
    path = tmpdir.mkdir("sub").join("hello.yml")
    path.write("content")
    init = {
        'src': str(path),
        'dst': str(path),
    }
    context = init
    disk_usage = DiskUsage(init)
    disk_usage.run(context)
    expected_result = {
        'title': disk_usage.title,
        'comment': disk_usage.comment,
        'type': disk_usage.type,
        'data': -1,
    }
    with patch.object(disk_usage, 'log_warning') as mock:
       disk_usage.run(context)
    mock.assert_called_with(f"{path} is not a directory. Returning -1.")
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result == result

def test_permission_error(tmpdir):
    path = str(tmpdir) + '/test.yml'
    forbidden = '/root'
    init = {
        'src': forbidden,
        'dst': str(path),
    }
    context = init
    disk_usage = DiskUsage(init)
    disk_usage.run(context)
    expected_result = {
        'title': disk_usage.title,
        'comment': disk_usage.comment,
        'type': disk_usage.type,
        'data': -1,
    }
    with patch.object(disk_usage, 'log_warning') as mock:
       disk_usage.run(context)
    mock.assert_called_with(f"No permission to open {forbidden}. Returning -1.")
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result == result
