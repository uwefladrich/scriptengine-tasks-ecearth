"""Tests for monitoring/nemo_global_mean_year_mean_timeseries.py"""

import cf_units
import iris
import numpy as np
import pytest
import scriptengine.exceptions

from monitoring.nemo_timeseries import (
    NemoGlobalMeanYearMeanTimeseries,
    NemoGlobalSumYearMeanTimeseries,
    NemoYearMeanTimeseries,
)


def test_load_collapse_save(tmp_path):
    # Tests for issue #53, caused by a bug in Iris 3.2.0.post0

    src = "tests/testdata/NEMO_output_sivolu-199003.nc"
    dst = tmp_path / "test.nc"
    var = "sivolu"

    cube = iris.load_cube(src, var).collapsed("latitude", iris.analysis.MEAN)
    #   print(cube)  # Workaround for the Iris bug
    iris.save(cube, str(dst))


def test_nemo_global_mean_year_mean_timeseries_working(tmp_path):
    init = {
        "src": ["./tests/testdata/NEMO_output_sivolu-199003.nc"],
        "dst": str(tmp_path / "test.nc"),
        "domain": "./tests/testdata/domain_cfg_example.nc",
        "varname": "sivolu",
        "grid": "T",
    }
    global_avg = NemoGlobalMeanYearMeanTimeseries(init)
    global_avg.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.name() == "sea_ice_thickness"
    assert cube.units == cf_units.Unit("m")  # no unit change
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.cell_methods == (
        iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
        iris.coords.CellMethod("mean", coords="area"),
    )


def test_nemo_global_sum_year_mean_timeseries_working(tmp_path):
    init = {
        "src": ["./tests/testdata/NEMO_output_sivolu-199003.nc"],
        "dst": str(tmp_path / "test.nc"),
        "domain": "./tests/testdata/domain_cfg_example.nc",
        "varname": "sivolu",
        "grid": "T",
    }
    global_avg = NemoGlobalSumYearMeanTimeseries(init)
    global_avg.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.name() == "sea_ice_thickness"
    assert cube.units == cf_units.Unit("m3")  # units were changed due to integration
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.cell_methods == (
        iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
        iris.coords.CellMethod("sum", coords="area"),
    )


def test_nemo_year_mean_timeseries_wrong_dim(tmp_path):
    init = {
        "src": ["./tests/testdata/NEMO_output_sivolu-199003.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    year_mean_ts = NemoYearMeanTimeseries(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        year_mean_ts.run,
        init,
    )


def test_nemo_year_mean_timeseries_working(tmp_path):
    init = {
        "src": ["./tests/testdata/a8gx_bgc_5d_bioscalar_1990-1990.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "tdenit",
    }
    year_mean_ts = NemoYearMeanTimeseries(init)
    year_mean_ts.run(init)
    out_cube = iris.load_cube(init["dst"])
    assert out_cube.shape == (1,)
    assert out_cube.coord().has_bounds()
    assert out_cube.cell_methods == (
        iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
    )
