"""Tests for monitoring/nemo_global_sum_year_mean_timeseries.py"""

import iris

from monitoring.nemo_global_sum_year_mean_timeseries import (
    NemoGlobalSumYearMeanTimeseries,
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
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.cell_methods == (
        iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
        iris.coords.CellMethod("sum", coords="area"),
    )
