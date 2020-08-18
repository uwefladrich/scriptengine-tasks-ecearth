"""Tests for scriptengine/tasks/ecearth/monitoring/ocean_dynamic_map.py"""

import iris

from scriptengine.tasks.ecearth.monitoring.ocean_dynamic_map import OceanDynamicMap

def test_ocean_dynamic_map_once(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_dynamic_map = OceanDynamicMap(init)
    ocean_dynamic_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == ocean_dynamic_map.map_type
    assert cube.attributes['type'] == ocean_dynamic_map.diagnostic_type

def test_ocean_dynamic_map_twice(tmpdir):
    init_a = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_dynamic_map = OceanDynamicMap(init_a)
    ocean_dynamic_map.run(init_a)
    init_b = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199009.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_dynamic_map = OceanDynamicMap(init_b)
    ocean_dynamic_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == ocean_dynamic_map.map_type
    assert cube.attributes['type'] == ocean_dynamic_map.diagnostic_type
