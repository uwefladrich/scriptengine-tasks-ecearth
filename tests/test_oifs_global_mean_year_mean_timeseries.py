"""Tests for scriptengine/tasks/ecearth/monitoring/oifs_global_mean_year_mean_timeseries.py"""

import pytest
import iris

import scriptengine.exceptions
from scriptengine.tasks.ecearth.monitoring.oifs_global_mean_year_mean_timeseries import OifsGlobalMeanYearMeanTimeseries

def test_oifs_global_mean_year_mean_timeseries_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmo_ts = OifsGlobalMeanYearMeanTimeseries(init)
    atmo_ts.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == 'time series'
    assert cube.cell_methods == (
        iris.coords.CellMethod('mean', coords='time', intervals='21600.0 seconds'),
        iris.coords.CellMethod('mean', coords='area'),
        )

def test_oifs_global_mean_year_mean_timeseries_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 0,
    }
    atmo_ts = OifsGlobalMeanYearMeanTimeseries(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        atmo_ts.run,
        init,
    )