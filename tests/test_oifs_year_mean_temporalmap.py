"""Tests for scriptengine/tasks/ecearth/monitoring/oifs_year_mean_temporalmap.py"""

import pytest
import iris

import scriptengine.exceptions
from scriptengine.tasks.ecearth.monitoring.oifs_year_mean_temporalmap import OifsYearMeanTemporalmap

def test_oifs_year_mean_temporalmap_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmos_time_map = OifsYearMeanTemporalmap(init)
    atmos_time_map.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == 'temporal map'
    assert cube.attributes['map_type'] == 'global atmosphere'


def test_oifs_year_mean_temporalmap_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 500,
    }
    atmos_time_map = OifsYearMeanTemporalmap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        atmos_time_map.run,
        init,
    )
