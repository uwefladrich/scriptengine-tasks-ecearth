"""Tests for scriptengine/tasks/ecearth/monitoring/ocean_time_map.py"""

import iris

from scriptengine.tasks.ecearth.monitoring.ocean_time_map import OceanTimeMap

def test_ocean_time_map_once(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = OceanTimeMap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == ocean_time_map.map_type
    assert cube.attributes['diagnostic_type'] == ocean_time_map.diagnostic_type

def test_ocean_time_map_twice(tmpdir):
    init_a = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = OceanTimeMap(init_a)
    ocean_time_map.run(init_a)
    init_b = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199009.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = OceanTimeMap(init_b)
    ocean_time_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == ocean_time_map.map_type
    assert cube.attributes['diagnostic_type'] == ocean_time_map.diagnostic_type
