"""Tests for scriptengine/tasks/ecearth/monitoring/atmosphere_static_map.py"""

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.atmosphere_dynamic_map import AtmosphereDynamicMap

def test_atmosphere_dynamic_map_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmo_dynamic_map = AtmosphereDynamicMap(init)
    atmo_dynamic_map.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['type'] == atmo_dynamic_map.diagnostic_type

def test_atmosphere_dynamic_map_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 0,
    }
    atmo_dynamic_map = AtmosphereDynamicMap(init)
    with patch.object(atmo_dynamic_map, 'log_error') as mock:
        atmo_dynamic_map.run(init)
    mock.assert_called_with(f"CF Phenomenon for {init['grib_code']} not found. Update local table?")
