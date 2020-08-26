"""Tests for scriptengine/tasks/ecearth/monitoring/nemo_all_mean_map.py"""

import iris

from scriptengine.tasks.ecearth.monitoring.nemo_all_mean_map import NemoAllMeanMap

def test_nemo_all_mean_map_once(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_map = NemoAllMeanMap(init)
    ocean_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == 'global ocean'
    assert cube.attributes['diagnostic_type'] == 'map'
    assert cube.coord('time').climatological
    assert len(cube.coord('time').points) == 1

def test_nemo_all_mean_map_twice(tmpdir):
    init_a = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_map = NemoAllMeanMap(init_a)
    ocean_map.run(init_a)
    init_b = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199103.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_map = NemoAllMeanMap(init_b)
    ocean_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == 'global ocean'
    assert cube.attributes['diagnostic_type'] == 'map'
    assert cube.coord('time').climatological
    assert len(cube.coord('time').points) == 1
