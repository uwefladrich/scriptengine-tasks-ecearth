"""Tests for monitoring/si3_hemis_point_month_mean_all_mean_map.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.si3_hemis_point_month_mean_all_mean_map import (
    Si3HemisPointMonthMeanAllMeanMap,
)


def test_ice_map_once(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    ice_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1


def test_ice_map_twice(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    ice_map.run(init)
    init["src"] = "./tests/testdata/NEMO_output_sivolu-199103.nc"
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    ice_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1


def test_ice_map_wrong_varname(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError, ice_map.run, init
    )


def test_ice_map_wrong_hemisphere(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError, ice_map.run, init
    )
