"""Tests for scriptengine/tasks/ecearth/monitoring/ice_time_series.py"""

import os

import pytest
import iris
import yaml
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.ice_time_series import SeaIceTimeSeries, meta_dict

def test_ice_time_series_dst_error():
    init = {
        "src": ["src_file.nc"],
        "dst": "dst_file.yml",
        "domain": "domain_file.nc",
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_time_series = SeaIceTimeSeries(init)
    with patch.object(ice_time_series, 'log_error') as mock:
       ice_time_series.run(init)
    mock.assert_called_with((
                f"{init['dst']} does not end in valid netCDF file extension. "
                f"Diagnostic can not be saved, returning now."))

def test_ice_time_series_working(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-03.nc', './tests/testdata/NEMO_output_sivolu-09.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_time_series = SeaIceTimeSeries(init)
    ice_time_series.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_ice_volume'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['type'] == 'time series'
    assert cube.cell_methods == (
        iris.coords.CellMethod('point', coords='time'),
        iris.coords.CellMethod('sum', coords='area', intervals='northern hemisphere'),
        )

def test_ice_time_series_wrong_varname(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-03.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "tos",
        "hemisphere": "south",
    }
    ice_time_series = SeaIceTimeSeries(init)
    ice_time_series.run(init)
    with patch.object(ice_time_series, 'log_error') as mock:
       ice_time_series.run(init)
    mock.assert_called_with((
                f"'varname' must be one of the following: {meta_dict.keys()} "
                f"Diagnostic will not be treated, returning now."))

def test_ice_time_series_wrong_hemisphere(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-03.nc', './tests/testdata/NEMO_output_sivolu-09.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_time_series = SeaIceTimeSeries(init)
    ice_time_series.run(init)
    with patch.object(ice_time_series, 'log_error') as mock:
       ice_time_series.run(init)
    mock.assert_called_with((
                f"'hemisphere' must be 'north' or 'south' but is '{init['hemisphere']}'."
                f"Diagnostic will not be treated, returning now."))

def test_ice_time_series_wrong_month(tmpdir):
    init = {
        "src": ['./tests/testdata/NEMO_output_sivolu-02.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_time_series = SeaIceTimeSeries(init)
    ice_time_series.run(init)
    with patch.object(ice_time_series, 'log_error') as mock:
       ice_time_series.run(init)
    mock.assert_called_with((
                f"FileNotFoundError: Month 03 not found in {init['src']}!."
                f"Diagnostic can not be created, returning now."))