"""Tests for scriptengine/tasks/ecearth/monitoring/ocean_static_map.py"""

import os
import datetime

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.ocean_static_map import OceanStaticMap

def test_ocean_map_once(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_static_map = OceanStaticMap(init)
    ocean_static_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == ocean_static_map.map_type
    assert cube.attributes['type'] == ocean_static_map.diagnostic_type
    assert cube.coord('time').climatological == True
    assert len(cube.coord('time').points) == 1

def test_ocean_map_twice(tmpdir):
    init_a = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_static_name = OceanStaticMap(init_a)
    ocean_static_name.run(init_a)
    init_b = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199103.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_static_name = OceanStaticMap(init_b)
    ocean_static_name.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == ocean_static_name.map_type
    assert cube.attributes['type'] == ocean_static_name.diagnostic_type
    assert cube.coord('time').climatological == True
    assert len(cube.coord('time').points) == 1
