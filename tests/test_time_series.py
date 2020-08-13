"""Tests for scriptengine/tasks/ecearth/monitoring/disk_usage.py"""

import os

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.time_series import TimeSeries

def test_time_series_dst_error():
    init = {
        "title": "A Test Diagnostic",
        "dst": "dst_file.yml",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = TimeSeries(init)
    with patch.object(time_series, 'log_error') as mock:
       time_series.run(init)
    mock.assert_called_with((
                f"{init['dst']} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."))

def test_monotonic_increase():
    init = {
        "title": "A Test Diagnostic",
        "dst": "dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = TimeSeries(init)

    old_coord = iris.coords.Coord([1])
    new_coord = iris.coords.Coord([2])
    assert time_series.test_monotonic_increase(old_coord, new_coord) == True
    assert time_series.test_monotonic_increase(new_coord, old_coord) == False

    old_coord_with_bounds = iris.coords.Coord([2], bounds=[0.5, 1.5])
    new_coord_with_bounds = iris.coords.Coord([1], bounds=[1.5, 2.5])
    assert time_series.test_monotonic_increase(old_coord_with_bounds, new_coord_with_bounds) == True
    assert time_series.test_monotonic_increase(new_coord_with_bounds, old_coord_with_bounds) == False

def test_time_series_first_save(tmpdir):
    init = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = TimeSeries(init)
    time_series.run(init)

    cube = iris.load_cube(init['dst'])
    assert cube.data == [init['data_value']]
    assert cube.coord().points == [init['coord_value']]
    assert cube.attributes['title'] == init['title']
    assert cube.attributes['type'] == 'time series'
    assert cube.name() == init['title']
    assert cube.units.name == '1'
    assert cube.coord().name() == 'time'
    assert cube.coord().units.name == '1'

def test_time_series_append(tmpdir):
    init_a = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = TimeSeries(init_a)
    time_series.run(init_a)

    init_b = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 1,
    }

    time_series = TimeSeries(init_b)
    time_series.run(init_b)

    cube = iris.load_cube(init_a['dst'])
    assert (cube.data == [init_a['data_value'], init_b['data_value']]).all()
    assert (cube.coord().points == [init_a['coord_value'], init_b['coord_value']]).all()
    assert cube.attributes['title'] == init_a['title']
    assert cube.attributes['type'] == 'time series'
    assert cube.name() == init_a['title']
    assert cube.coord().name() == 'time'
    assert cube.units.name == '1'
    assert cube.coord().units.name == '1'
