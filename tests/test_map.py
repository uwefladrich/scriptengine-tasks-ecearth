"""Tests for scriptengine/tasks/ecearth/monitoring/map.py"""

from scriptengine.tasks.ecearth.monitoring.map import Map

def test_map_dst_error():
    test_map = Map({})
    assert not test_map.correct_file_extension("test.yml")
