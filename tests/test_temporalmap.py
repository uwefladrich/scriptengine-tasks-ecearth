"""Tests for scriptengine/tasks/ecearth/monitoring/temporalmap.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.temporalmap import Temporalmap

def test_time_map_dst_error():
    time_map = Temporalmap({})
    assert time_map.correct_file_extension("test.yml") == False


def test_presentation_value_range():
    
    time_map = Temporalmap({})
    cube = iris.cube.Cube([0, 10])

    cube.attributes['presentation_min'] = None
    cube.attributes['presentation_max'] = None
    cube = time_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == -1
    assert cube.attributes['presentation_max'] == 11

    cube.attributes['presentation_min'] = 0
    cube.attributes['presentation_max'] = None
    cube = time_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == 0
    assert cube.attributes['presentation_max'] == 11

    cube.attributes['presentation_min'] = None
    cube.attributes['presentation_max'] = 10
    cube = time_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == -1
    assert cube.attributes['presentation_max'] == 10

    cube.attributes['presentation_min'] = 0
    cube.attributes['presentation_max'] = 10
    cube = time_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == 0
    assert cube.attributes['presentation_max'] == 10
