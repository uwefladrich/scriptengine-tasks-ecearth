"""Tests for scriptengine/tasks/ecearth/monitoring/temporalmap.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.temporalmap import Temporalmap

def test_time_map_dst_error():
    time_map = Temporalmap({})
    assert time_map.correct_file_extension("test.yml") == False
