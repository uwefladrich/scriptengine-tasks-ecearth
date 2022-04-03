"""Tests for monitoring/oifs_year_mean_temporalmap.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.oifs_year_mean_temporalmap import OifsYearMeanTemporalmap


def test_oifs_year_mean_temporalmap_working(tmp_path):
    init = {
        "src": ["./tests/testdata/TES1_atm_1m_1990_2t.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "2t",
    }
    atmos_time_map = OifsYearMeanTemporalmap(init)
    atmos_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.name() == "2 metre temperature"
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "temporal map"
    assert cube.attributes["map_type"] == "global atmosphere"


def test_oifs_year_mean_temporalmap_wrong_varname(tmp_path):
    init = {
        "src": ["./tests/testdata/TES1_atm_1m_1990_2t.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    atmos_time_map = OifsYearMeanTemporalmap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        atmos_time_map.run,
        init,
    )
