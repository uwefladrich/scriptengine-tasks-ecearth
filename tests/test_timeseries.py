"""Tests for monitoring/timeseries.py"""

import datetime
from pathlib import Path

import iris
import pytest
import scriptengine.exceptions

from monitoring.timeseries import Timeseries


def test_timeseries_dst_error():
    init = {
        "title": "A Test Diagnostic",
        "dst": "dst_file.yml",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        time_series.check_file_extension,
        Path(init["dst"]),
    )


def test_monotonic_increase():
    init = {
        "title": "A Test Diagnostic",
        "dst": "dst_file.nc",
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init)

    old_coord = iris.coords.DimCoord([1])
    new_coord = iris.coords.DimCoord([2])
    assert time_series.test_monotonic_increase(old_coord, new_coord) is None
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        time_series.test_monotonic_increase,
        new_coord,
        old_coord,
    )

    old_coord_with_bounds = iris.coords.DimCoord([1], bounds=[0.5, 1.5])
    new_coord_with_bounds = iris.coords.DimCoord([2], bounds=[1.5, 2.5])
    assert (
        time_series.test_monotonic_increase(
            old_coord_with_bounds, new_coord_with_bounds
        )
        is None
    )
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        time_series.test_monotonic_increase,
        new_coord_with_bounds,
        old_coord_with_bounds,
    )


def test_time_series_first_save(tmp_path):
    init = {
        "title": "A Test Diagnostic",
        "dst": str(tmp_path / "dst_file.nc"),
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init)
    time_series.run(init)

    cube = iris.load_cube(init["dst"])
    assert cube.data == [init["data_value"]]
    assert cube.coord().points == [init["coord_value"]]
    assert cube.attributes["title"] == init["title"]
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.name() == init["title"]
    assert cube.units.name == "1"
    assert cube.coord().name() == "time"
    assert cube.coord().units.name == "1"


def test_time_series_append(tmp_path):
    init_a = {
        "title": "A Test Diagnostic",
        "dst": str(tmp_path / "dst.nc"),
        "data_value": 0,
        "coord_value": 0,
    }
    time_series = Timeseries(init_a)
    time_series.run(init_a)

    init_b = init_a.copy()
    init_b["coord_value"] = 1
    time_series = Timeseries(init_b)
    time_series.run(init_b)

    cube = iris.load_cube(init_a["dst"])
    assert (cube.data == [init_a["data_value"], init_b["data_value"]]).all()
    assert (cube.coord().points == [init_a["coord_value"], init_b["coord_value"]]).all()
    assert cube.attributes["title"] == init_a["title"]
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.name() == init_a["title"]
    assert cube.coord().name() == "time"
    assert cube.units.name == "1"
    assert cube.coord().units.name == "1"


def test_time_series_append_nonmonotonic(tmp_path):
    init = {
        "title": "A Test Diagnostic",
        "dst": str(tmp_path / "dst_file.nc"),
        "data_value": 0,
        "coord_value": 1,
    }
    time_series = Timeseries(init)
    time_series.run(init)

    init["coord_value"] = 0

    time_series = Timeseries(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        time_series.run,
        init,
    )


def test_time_series_date_time(tmp_path):
    seconds_value = (
        datetime.datetime(1990, 1, 1) - datetime.datetime(1900, 1, 1)
    ).total_seconds()
    init_date = {
        "title": "A Date Diagnostic",
        "dst": str(tmp_path / "date_file.nc"),
        "data_value": 0,
        "coord_value": "1990-01-01",
    }
    time_series = Timeseries(init_date)
    time_series.run(init_date)

    cube = iris.load_cube(init_date["dst"])
    assert cube.data == [init_date["data_value"]]
    assert cube.coord().points == [seconds_value]
    assert cube.attributes["title"] == init_date["title"]
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.name() == init_date["title"]
    assert cube.units.name == "1"
    assert cube.coord().name() == "time"
    assert cube.coord().units.name == "second since 1900-01-01 00:00:00.0000000 UTC"

    init_date_time = {
        "title": "A Datetime Diagnostic",
        "dst": str(tmp_path / "date_time_file.nc"),
        "data_value": 0,
        "coord_value": "1990-01-01 00:00:00",
    }
    time_series = Timeseries(init_date_time)
    time_series.run(init_date_time)

    cube = iris.load_cube(init_date_time["dst"])
    assert cube.data == [init_date_time["data_value"]]
    assert cube.coord().points == [seconds_value]
    assert cube.attributes["title"] == init_date_time["title"]
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.name() == init_date_time["title"]
    assert cube.units.name == "1"
    assert cube.coord().name() == "time"
    assert cube.coord().units.name == "second since 1900-01-01 00:00:00.0000000 UTC"
