"""Tests for monitoring/si3_hemis_point_month_mean_all_mean_map.py"""

import iris
import pytest

import scriptengine.exceptions
from monitoring.si3_hemis_point_month_mean_all_mean_map import Si3HemisPointMonthMeanAllMeanMap

def test_ice_map_once(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    ice_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == 'polar ice sheet'
    assert cube.attributes['diagnostic_type'] == 'map'
    assert cube.coord('time').climatological
    assert len(cube.coord('time').points) == 1

def test_ice_map_twice(tmpdir):
    init_a = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init_a)
    ice_map.run(init_a)
    init_b = {
        "src": './tests/testdata/NEMO_output_sivolu-199103.nc',
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init_b)
    ice_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == 'polar ice sheet'
    assert cube.attributes['diagnostic_type'] == 'map'
    assert cube.coord('time').climatological
    assert len(cube.coord('time').points) == 1

def test_ice_map_wrong_varname(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        ice_map.run,
        init
    )

def test_ice_map_wrong_hemisphere(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        ice_map.run,
        init
    )
