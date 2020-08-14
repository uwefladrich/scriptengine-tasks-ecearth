"""Tests for scriptengine/tasks/ecearth/monitoring/global_average.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.global_average import GlobalAverage

def test_global_average_working(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
    }
    global_avg = GlobalAverage(init)
    global_avg.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_ice_thickness'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['type'] == 'time series'
    assert cube.cell_methods == (
        iris.coords.CellMethod('mean', coords='time', intervals='1 month'),
        iris.coords.CellMethod('mean', coords='area'),
        )

