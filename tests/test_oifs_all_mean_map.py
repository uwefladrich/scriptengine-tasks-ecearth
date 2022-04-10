"""Tests for monitoring/oifs_all_mean_map.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.oifs_all_mean_map import OifsAllMeanMap


def test_oifs_all_mean_map_working(tmp_path):
    init = {
        "src": ["./tests/testdata/TES1_atm_1m_1990_2t.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "2t",
    }
    atmo_map = OifsAllMeanMap(init)
    atmo_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.name() == "2 metre temperature"
    assert cube.attributes["title"] is not None
    assert cube.attributes["comment"] is not None
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.attributes["map_type"] == "global atmosphere"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1


def test_oifs_all_mean_map_wrong_code(tmp_path):
    init = {
        "src": ["./tests/testdata/TES1_atm_1m_1990_2t.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    atmo_map = OifsAllMeanMap(init)

    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError, atmo_map.run, init
    )
