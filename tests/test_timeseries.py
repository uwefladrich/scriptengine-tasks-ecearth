"""Tests for scriptengine/tasks/ecearth/monitoring/timeseries.py"""

import datetime
from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.timeseries import Timeseries

def test_time_series_dst_error():
    init = {
        "title": "A Test Diagnostic",
        "dst": "dst_file.yml",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init)
    assert not time_series.correct_file_extension(init['dst'])

def test_monotonic_increase():
    init = {
        "title": "A Test Diagnostic",
        "dst": "dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init)

    old_coord = iris.coords.Coord([1])
    new_coord = iris.coords.Coord([2])
    assert time_series.test_monotonic_increase(old_coord, new_coord)
    assert not time_series.test_monotonic_increase(new_coord, old_coord)

    old_coord_with_bounds = iris.coords.Coord([2], bounds=[0.5, 1.5])
    new_coord_with_bounds = iris.coords.Coord([1], bounds=[1.5, 2.5])
    assert time_series.test_monotonic_increase(old_coord_with_bounds, new_coord_with_bounds)
    assert not time_series.test_monotonic_increase(new_coord_with_bounds, old_coord_with_bounds)

def test_time_series_first_save(tmpdir):
    init = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init)
    time_series.run(init)

    cube = iris.load_cube(init['dst'])
    assert cube.data == [init['data_value']]
    assert cube.coord().points == [init['coord_value']]
    assert cube.attributes['title'] == init['title']
    assert cube.attributes['diagnostic_type'] == 'time series'
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
    time_series = Timeseries(init_a)
    time_series.run(init_a)

    init_b = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 1,
    }

    time_series = Timeseries(init_b)
    time_series.run(init_b)

    cube = iris.load_cube(init_a['dst'])
    assert (cube.data == [init_a['data_value'], init_b['data_value']]).all()
    assert (cube.coord().points == [init_a['coord_value'], init_b['coord_value']]).all()
    assert cube.attributes['title'] == init_a['title']
    assert cube.attributes['diagnostic_type'] == 'time series'
    assert cube.name() == init_a['title']
    assert cube.coord().name() == 'time'
    assert cube.units.name == '1'
    assert cube.coord().units.name == '1'

def test_time_series_append_nonmonotonic(tmpdir):
    init_a = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 1,
    }
    time_series = Timeseries(init_a)
    time_series.run(init_a)

    init_b = {
        "title": "A Test Diagnostic",
        "dst": str(tmpdir) + "/dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }

    time_series = Timeseries(init_b)
    with patch.object(time_series, 'log_warning') as mock:
        time_series.run(init_b)
    mock.assert_called_with("Non-monotonic coordinate. Cube will not be saved.")
    


def test_time_series_date_time(tmpdir):
    seconds_value = (datetime.datetime(1990, 1, 1) - datetime.datetime(1900, 1, 1)).total_seconds()
    init_date = {
        "title": "A Date Diagnostic",
        "dst": str(tmpdir) + "/date_file.nc",
        "data_value": 0,
        "coord_value": "1990-01-01",
    }
    time_series = Timeseries(init_date)
    time_series.run(init_date)
    
    cube = iris.load_cube(init_date['dst'])
    assert cube.data == [init_date['data_value']]
    assert cube.coord().points == [seconds_value]
    assert cube.attributes['title'] == init_date['title']
    assert cube.attributes['diagnostic_type'] == 'time series'
    assert cube.name() == init_date['title']
    assert cube.units.name == '1'
    assert cube.coord().name() == 'time'
    assert cube.coord().units.name == "second since 1900-01-01 00:00:00.0000000 UTC"

    init_date_time = {
        "title": "A Datetime Diagnostic",
        "dst": str(tmpdir) + "/date_time_file.nc",
        "data_value": 0,
        "coord_value": "1990-01-01 00:00:00",
    }
    time_series = Timeseries(init_date_time)
    time_series.run(init_date_time)
    
    cube = iris.load_cube(init_date_time['dst'])
    assert cube.data == [init_date_time['data_value']]
    assert cube.coord().points == [seconds_value]
    assert cube.attributes['title'] == init_date_time['title']
    assert cube.attributes['diagnostic_type'] == 'time series'
    assert cube.name() == init_date_time['title']
    assert cube.units.name == '1'
    assert cube.coord().name() == 'time'
    assert cube.coord().units.name == "second since 1900-01-01 00:00:00.0000000 UTC"
