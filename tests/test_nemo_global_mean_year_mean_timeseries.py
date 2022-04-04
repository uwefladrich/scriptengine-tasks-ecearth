"""Tests for monitoring/nemo_global_mean_year_mean_timeseries.py"""

import iris

from monitoring.nemo_global_mean_year_mean_timeseries import (
    NemoGlobalMeanYearMeanTimeseries,
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
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.cell_methods == (
        iris.coords.CellMethod("mean", coords="time", intervals="1 month"),
        iris.coords.CellMethod("mean", coords="area"),
    )
