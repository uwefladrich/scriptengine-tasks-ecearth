"""Tests for scriptengine/tasks/ecearth/monitoring/disk_usage.py"""

import os
import datetime

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.dynamic_map import DynamicMap

def test_dynamic_map_dst_error():
    dynamic_map = DynamicMap({})
    assert dynamic_map.correct_file_extension("test.yml") == False


def test_presentation_value_range():
    
    dynamic_map = DynamicMap({})
    cube = iris.cube.Cube([0, 10])

    cube.attributes['presentation_min'] = None
    cube.attributes['presentation_max'] = None
    cube = dynamic_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == -1
    assert cube.attributes['presentation_max'] == 11

    cube.attributes['presentation_min'] = 0
    cube.attributes['presentation_max'] = None
    cube = dynamic_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == 0
    assert cube.attributes['presentation_max'] == 11

    cube.attributes['presentation_min'] = None
    cube.attributes['presentation_max'] = 10
    cube = dynamic_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == -1
    assert cube.attributes['presentation_max'] == 10

    cube.attributes['presentation_min'] = 0
    cube.attributes['presentation_max'] = 10
    cube = dynamic_map.set_presentation_value_range(cube)
    assert cube.attributes['presentation_min'] == 0
    assert cube.attributes['presentation_max'] == 10
