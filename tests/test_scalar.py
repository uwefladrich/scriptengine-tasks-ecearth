"""Tests for scriptengine/tasks/ecearth/monitoring/scalar.py"""

import os

import pytest
import yaml
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.scalar import Scalar 

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
def test_scalar_working(tmpdir, init, context, expected_result):
    path = str(tmpdir + '/test.yml')
    init['dst'] = path
    context['dst'] = path
    scalar = Scalar(init)
    scalar.run(context)
    with open(path) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result == result


def test_scalar_runtime_error(tmpdir):
    path = str(tmpdir + '/test.yml')
    init = {
        'title': 'Title',
        'comment': 'Comment',
        'dst': path,
    }
    pytest.raises(
        RuntimeError,
        Scalar,
        init,
        )

def test_scalar_extension_error(tmpdir):
    path = str(tmpdir + '/test.nc')
    init = {
        'title': 'Title',
        'comment': 'Comment',
        'value': 'Value',
        'dst': path,
    }
    context = init
    scalar = Scalar(init)
    with patch.object(scalar, 'log_warning') as mock:
       scalar.run(context)
    mock.assert_called_with((
                f"{path} does not end in valid YAML file extension. "
                f"Diagnostic will not be saved."))
    