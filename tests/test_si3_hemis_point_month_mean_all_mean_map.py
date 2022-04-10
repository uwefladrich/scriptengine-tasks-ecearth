"""Tests for monitoring/si3_hemis_point_month_mean_all_mean_map.py"""

import iris
from iris.cube import Cube

from monitoring.si3_hemis_point_month_mean_all_mean_map import (
    Si3HemisPointMonthMeanAllMeanMap,
    _set_cell_methods,
)


def test_ice_map_once(tmp_path):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run({})
    cube = iris.load_cube(args["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1


def test_ice_map_twice(tmp_path):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run(args)
    args["src"] = "./tests/testdata/NEMO_output_sivolu-199103.nc"
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run(args)
    cube = iris.load_cube(args["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1


def test_ice_map_wrong_varname(tmp_path, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run({})
    assert "Invalid varname " in caplog.text


def test_ice_map_wrong_hemisphere(tmp_path, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run({})
    assert "Invalid hemisphere " in caplog.text


def test_set_cell_methods():
    cube = Cube([])
    assert cube.cell_methods == ()
    cube = _set_cell_methods(cube, "north")
    assert cube.cell_methods != ()
