"""Tests for scriptengine/tasks/ecearth/monitoring/nemo_global_mean_year_mean_timeseries.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.nemo_global_mean_year_mean_timeseries import NemoGlobalMeanYearMeanTimeseries

def test_nemo_global_mean_year_mean_timeseries_working(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
        "grid": "T",
    }
    global_avg = NemoGlobalMeanYearMeanTimeseries(init)
    global_avg.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_ice_thickness'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == 'time series'
    assert cube.cell_methods == (
        iris.coords.CellMethod('mean', coords='time', intervals='1 month'),
        iris.coords.CellMethod('mean', coords='area'),
        )
