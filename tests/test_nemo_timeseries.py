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
    dim_coord = iris.coords.DimCoord(
        [1.0, 2.0],
        bounds=[[0.5, 1.5], [1.5, 2.5]],
        standard_name="time",
        var_name="time",
    )
    aux_coord = iris.coords.AuxCoord([1, 2], standard_name="time", var_name="aux_time")
    cube = iris.cube.Cube(
        [0.0, 1.0],
        dim_coords_and_dims=[(dim_coord, 0)],
        aux_coords_and_dims=[(aux_coord, 0)],
        var_name="data",
    )
    in_cube_path = tmp_path / "test_in.nc"
    iris.save(cube, in_cube_path)
    init = {
        "src": [in_cube_path],
        "dst": str(tmp_path / "test_out.nc"),
        "varname": "data",
    }
    year_mean_ts = NemoYearMeanTimeseries(init)
    year_mean_ts.run(init)

    out_cube = iris.load_cube(init["dst"])
    assert out_cube.shape == (1,)
    assert out_cube.coord().has_bounds()
    assert np.all(
        out_cube.coord().bounds
        == np.array([dim_coord.bounds[0, 0], dim_coord.bounds[-1, -1]])
    )
    assert out_cube.coord().points[0] == np.mean(dim_coord.points)
