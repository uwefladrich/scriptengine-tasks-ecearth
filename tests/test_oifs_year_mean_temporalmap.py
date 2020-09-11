"""Tests for scriptengine/tasks/ecearth/monitoring/oifs_year_mean_temporalmap.py"""

from unittest.mock import patch

import iris

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
    with patch.object(atmos_time_map, 'log_warning') as mock:
        atmos_time_map.run(init)
    mock.assert_called_with(f"CF Phenomenon for {init['grib_code']} not found. Update local table?")
