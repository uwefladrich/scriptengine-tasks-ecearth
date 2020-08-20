"""Tests for scriptengine/tasks/ecearth/monitoring/atmosphere_time_series.py"""

from unittest.mock import patch
import iris

from scriptengine.tasks.ecearth.monitoring.atmosphere_time_series import AtmosphereTimeSeries

def test_atmosphere_time_series_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmo_ts = AtmosphereTimeSeries(init)
    atmo_ts.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == atmo_ts.diagnostic_type
    assert cube.cell_methods == (
        iris.coords.CellMethod('mean', coords='time', intervals='6.0 hours'),
        iris.coords.CellMethod('mean', coords='area'),
        )

def test_atmosphere_time_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 0,
    }
    atmo_ts = AtmosphereTimeSeries(init)
    with patch.object(atmo_ts, 'log_warning') as mock:
        atmo_ts.run(init)
    mock.assert_called_with(f"CF Phenomenon for {init['grib_code']} not found. Update local table?")
