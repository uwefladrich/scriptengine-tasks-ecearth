"""Tests for scriptengine/tasks/ecearth/monitoring/ice_dynamic_map.py"""

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.ice_dynamic_map import SeaIceDynamicMap, meta_dict

def test_ice_dynamic_map_once(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_dynamic_map = SeaIceDynamicMap(init)
    ice_dynamic_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == ice_dynamic_map.map_type
    assert cube.attributes['type'] == ice_dynamic_map.diagnostic_type

def test_ice_dynamic_map_twice(tmpdir):
    init_a = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_dynamic_map = SeaIceDynamicMap(init_a)
    ice_dynamic_map.run(init_a)
    init_b = {
        "src": './tests/testdata/NEMO_output_sivolu-199103.nc',
        "dst": str(tmpdir) + '/test.nc',
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_dynamic_map = SeaIceDynamicMap(init_b)
    ice_dynamic_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == ice_dynamic_map.map_type
    assert cube.attributes['type'] == ice_dynamic_map.diagnostic_type

def test_ice_dynamic_map_wrong_varname(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_dynamic_map = SeaIceDynamicMap(init)
    ice_dynamic_map.run(init)
    with patch.object(ice_dynamic_map, 'log_error') as mock:
       ice_dynamic_map.run(init)
    mock.assert_called_with((
                f"'varname' must be one of the following: {meta_dict.keys()} "
                f"Diagnostic will not be treated, returning now."))

def test_ice_dynamic_map_wrong_hemisphere(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_dynamic_map = SeaIceDynamicMap(init)
    ice_dynamic_map.run(init)
    with patch.object(ice_dynamic_map, 'log_error') as mock:
       ice_dynamic_map.run(init)
    mock.assert_called_with((
                f"'hemisphere' must be 'north' or 'south' but is '{init['hemisphere']}'."
                f"Diagnostic will not be treated, returning now."))

# missing: wrong dst (covered by test_dynamic_map.py)
# missing: 'convert_to' test (requires a siconc input file) or multiple Mocks
