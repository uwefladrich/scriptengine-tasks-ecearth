"""Tests for scriptengine/tasks/ecearth/monitoring/write_scalar.py"""

import os

import pytest
import yaml
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.write_scalar import WriteScalar 

init = [
    {
        'title': 'Title',
        'value': 'Value',
        'comment': 'Comment',
    },
    {
        'title': 'Title',
        'value': [1, 2, 3],
    },
    {
        'title': 'Title',
        'value': '{{msg}}',
    },
]

context = [
    {
        'title': 'Title',
        'value': 'Value',
        'comment': 'Comment',
    },
    {
        'title': 'Title',
        'value': [1, 2, 3],
    },
    {
        'title': 'Title',
        'value': '{{msg}}',
        'msg': 'message',
    },
]

expected_result = [
    {
        'title': 'Title',
        'data': 'Value',
        'comment': 'Comment',
        'type': 'scalar',
    },
    {
        'title': 'Title',
        'data': [1, 2, 3],
        'type': 'scalar',
    },
    {
        'title': 'Title',
        'data': 'message',
        'type': 'scalar',
    },
]

@pytest.mark.parametrize("init, context, expected_result", zip(init, context, expected_result))
def test_write_scalar_working(tmpdir, init, context, expected_result):
    path = str(tmpdir + '/test.yml')
    init['dst'] = path
    context['dst'] = path
    write_scalar = WriteScalar(init)
    write_scalar.run(context)
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result == result


def test_write_scalar_runtime_error(tmpdir):
    path = str(tmpdir + '/test.yml')
    init = {
        'title': 'Title',
        'comment': 'Comment',
        'dst': path,
    }
    pytest.raises(
        RuntimeError,
        WriteScalar,
        init,
        )

def test_write_scalar_extension_error(tmpdir):
    path = str(tmpdir + '/test.nc')
    init = {
        'title': 'Title',
        'comment': 'Comment',
        'value': 'Value',
        'dst': path,
    }
    context = init
    write_scalar = WriteScalar(init)
    with patch.object(write_scalar, 'log_warning') as mock:
       write_scalar.run(context)
    mock.assert_called_with((
                f"{path} does not end in valid YAML file extension. "
                f"Diagnostic will not be saved."))
    