"""Tests for monitoring/temporalmap.py"""

import pytest
import scriptengine.exceptions

from monitoring.temporalmap import Temporalmap


def test_temporalmap_dst_error():
    temporalmap = Temporalmap({})
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        temporalmap.check_file_extension,
        "test.yml",
    )


def test_temporalmap_run():
    temporalmap = Temporalmap({})
    pytest.raises(NotImplementedError, temporalmap.run, {})
