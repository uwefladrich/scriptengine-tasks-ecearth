"""Tests for scriptengine/tasks/ecearth/monitoring/atmosphere_time_map.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.atmosphere_time_map import AtmosphereTimeMap

def test_atmosphere_time_map_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmos_time_map = AtmosphereTimeMap(init)
    atmos_time_map.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == atmos_time_map.diagnostic_type

def test_atmosphere_time_map_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 500,
    }
    atmos_time_map = AtmosphereTimeMap(init)
    with patch.object(atmos_time_map, 'log_warning') as mock:
        atmos_time_map.run(init)
    mock.assert_called_with(f"CF Phenomenon for {init['grib_code']} not found. Update local table?")
