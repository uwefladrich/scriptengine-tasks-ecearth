"""Tests for scriptengine/tasks/ecearth/monitoring/atmosphere_static_map.py"""

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.atmosphere_static_map import AtmosphereStaticMap

def test_atmosphere_map_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmo_map = AtmosphereStaticMap(init)
    atmo_map.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['type'] == atmo_map.diagnostic_type
    assert cube.coord('time').climatological == True
    assert len(cube.coord('time').points) == 1

def test_atmosphere_map_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 0,
    }
    atmo_map = AtmosphereStaticMap(init)
    with patch.object(atmo_map, 'log_error') as mock:
        atmo_map.run(init)
    mock.assert_called_with(f"CF Phenomenon for {init['grib_code']} not found. Update local table?")
