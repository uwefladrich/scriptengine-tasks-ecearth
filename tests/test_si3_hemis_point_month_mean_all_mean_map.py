"""Tests for scriptengine/tasks/ecearth/monitoring/si3_hemis_point_month_mean_all_mean_map.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.si3_hemis_point_month_mean_all_mean_map import Si3HemisPointMonthMeanAllMeanMap, meta_dict

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
    ice_map.run(init)
    with patch.object(ice_map, 'log_warning') as mock:
        ice_map.run(init)
    mock.assert_called_with((
                f"'varname' must be one of the following: {meta_dict.keys()} "
                f"Diagnostic will not be treated, returning now."))

def test_ice_map_wrong_hemisphere(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    ice_map.run(init)
    with patch.object(ice_map, 'log_warning') as mock:
        ice_map.run(init)
    mock.assert_called_with((
                f"'hemisphere' must be 'north' or 'south' but is '{init['hemisphere']}'."
                f"Diagnostic will not be treated, returning now."))

# missing: wrong dst (covered by test_map.py)
