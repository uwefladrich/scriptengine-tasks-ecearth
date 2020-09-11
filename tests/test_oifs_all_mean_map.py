"""Tests for scriptengine/tasks/ecearth/monitoring/oifs_all_mean_map.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.oifs_all_mean_map import OifsAllMeanMap

def test_oifs_all_mean_map_working(tmpdir):
    init = {
        "src": ['./tests/testdata/OIFSGG34199001'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 34,
    }
    atmo_map = OifsAllMeanMap(init)
    atmo_map.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == 'map'
    assert cube.attributes['map_type'] == 'global atmosphere'
    assert cube.coord('time').climatological
    assert len(cube.coord('time').points) == 1

def test_oifs_all_mean_map_wrong_code(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "grib_code": 500,
    }
    atmo_map = OifsAllMeanMap(init)
    with patch.object(atmo_map, 'log_warning') as mock:
        atmo_map.run(init)
    mock.assert_called_with(f"CF Phenomenon for {init['grib_code']} not found. Update local table?")
