"""Tests for monitoring/si3_hemis_sum_month_mean_timeseries.py"""

import iris
from iris.cube import Cube

from monitoring.si3_hemis_sum_month_mean_timeseries import (
    Si3HemisSumMonthMeanTimeseries,
    _set_cell_methods,
)


def test_si3_hemis_sum_month_mean_timeseries_working(tmp_path):
    args = {
        "src": [
            "./tests/testdata/NEMO_output_sivolu-199003.nc",
            "./tests/testdata/NEMO_output_sivolu-199009.nc",
        ],
        "dst": str(tmp_path / "test.nc"),
        "domain": "./tests/testdata/domain_cfg_example.nc",
        "varname": "sivolu",
        "hemisphere": "north",
        "month": 3,
    }
    ice_time_series = Si3HemisSumMonthMeanTimeseries(args)
    ice_time_series.run(args)
    cube = iris.load_cube(args["dst"])
    assert cube.name() == "sea_ice_volume"
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.cell_methods == (
        iris.coords.CellMethod("point", coords="time"),
        iris.coords.CellMethod("sum", coords="area", intervals="northern hemisphere"),
    )


def test_si3_hemis_sum_month_mean_timeseries_wrong_varname(tmp_path, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "domain": "./tests/testdata/domain_cfg_example.nc",
        "varname": "foo",
        "hemisphere": "south",
        "month": 3,
    }
    ice_time_series = Si3HemisSumMonthMeanTimeseries(args)
    ice_time_series.run({})
    assert "Invalid varname " in caplog.text


def test_si3_hemis_sum_month_mean_timeseries_wrong_hemisphere(tmp_path, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "domain": "./tests/testdata/domain_cfg_example.nc",
        "varname": "sivolu",
        "hemisphere": "foo",
        "month": 3,
    }
    ice_time_series = Si3HemisSumMonthMeanTimeseries(args)
    ice_time_series.run({})
    assert "Invalid hemisphere " in caplog.text


def test_set_cell_methods():
    cube = Cube([])
    assert cube.cell_methods == ()
    cube = _set_cell_methods(cube, "north")
    assert cube.cell_methods != ()
