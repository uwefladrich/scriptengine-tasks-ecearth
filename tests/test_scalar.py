"""Tests for monitoring/scalar.py"""

import pytest
import scriptengine.exceptions
import yaml

from monitoring.scalar import Scalar

init = [
    {
        "title": "Title",
        "value": "Value",
        "comment": "Comment",
    },
    {
        "title": "Title",
        "value": [1, 2, 3],
    },
    {
        "title": "Title",
        "value": "{{msg}}",
    },
]

context = [
    {
        "title": "Title",
        "value": "Value",
        "comment": "Comment",
    },
    {
        "title": "Title",
        "value": [1, 2, 3],
    },
    {
        "title": "Title",
        "value": "{{msg}}",
        "msg": "message",
    },
]

expected_result = [
    {
        "title": "Title",
        "value": "Value",
        "comment": "Comment",
        "diagnostic_type": "scalar",
    },
    {
        "title": "Title",
        "value": [1, 2, 3],
        "diagnostic_type": "scalar",
    },
    {
        "title": "Title",
        "value": "message",
        "diagnostic_type": "scalar",
    },
]


@pytest.mark.parametrize(
    "init, context, expected_result", zip(init, context, expected_result)
)
def test_scalar_working(tmp_path, init, context, expected_result):
    path = tmp_path / "test.yml"
    init["dst"] = str(path)
    context["dst"] = path
    scalar = Scalar(init)
    scalar.run(context)
    with path.open() as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    assert expected_result == result


def test_scalar_runtime_error(tmp_path):
    path = tmp_path / "test.yml"
    init = {
        "title": "Title",
        "comment": "Comment",
        "dst": str(path),
    }
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentMissingError,
        Scalar,
        init,
    )


def test_scalar_extension_error(tmp_path):
    path = tmp_path / "test.nc"
    init = {
        "title": "Title",
        "comment": "Comment",
        "value": "Value",
        "dst": str(path),
    }
    context = init
    scalar = Scalar(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        scalar.run,
        context,
    )
