"""Tests for monitoring/temporalmap.py"""

import pytest

import scriptengine.exceptions
from monitoring.temporalmap import Temporalmap

def test_time_map_dst_error():
    time_map = Temporalmap({})
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        time_map.check_file_extension,
        'test.yml',
    )
