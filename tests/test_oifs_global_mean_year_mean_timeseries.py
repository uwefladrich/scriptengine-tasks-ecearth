"""Tests for monitoring/oifs_global_mean_year_mean_timeseries.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.oifs_global_mean_year_mean_timeseries import (
    OifsGlobalMeanYearMeanTimeseries,
)


def test_oifs_global_mean_year_mean_timeseries_working(tmp_path):
    init = {
        "src": ["./tests/testdata/TES1_atm_1m_1990_2t.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "2t",
    }
    atmo_ts = OifsGlobalMeanYearMeanTimeseries(init)
    atmo_ts.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.name() == "2 metre temperature"
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "time series"
    assert cube.cell_methods == (
        iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
        iris.coords.CellMethod("mean", coords="area"),
    )


def test_oifs_global_mean_year_mean_timeseries_wrong_varname(tmp_path):
    init = {
        "src": ["./tests/testdata/TES1_atm_1m_1990_2t.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    atmo_ts = OifsGlobalMeanYearMeanTimeseries(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        atmo_ts.run,
        init,
    )
