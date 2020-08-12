"""Tests for scriptengine/tasks/ecearth/monitoring/disk_usage.py"""

import os

import pytest
import iris
import yaml
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.global_average import GlobalAverage




def test_global_average_dst_error():
    init = {
        "src": ["src_file.nc"],
        "dst": "dst_file.yml",
        "domain": "domain_file.nc",
        "varname": "tos",
    }
    global_avg = GlobalAverage(init)
    with patch.object(global_avg, 'log_error') as mock:
       global_avg.run(init)
    mock.assert_called_with((
                f"{init['dst']} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."))

def test_global_average_working(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_tos_example.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "tos",
    }
    global_avg = GlobalAverage(init)
    global_avg.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_surface_temperature'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['type'] == 'time series'
    assert cube.cell_methods == (
        iris.coords.CellMethod('mean', coords='time', intervals='1 month'),
        iris.coords.CellMethod('mean', coords='area'),
        )

