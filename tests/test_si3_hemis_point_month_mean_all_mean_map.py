"""Tests for monitoring/si3_hemis_point_month_mean_all_mean_map.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.si3_hemis_point_month_mean_all_mean_map import (
    Si3HemisPointMonthMeanAllMeanMap,
)


def test_ice_map_once(tmpdir):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
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


def test_ice_map_twice(tmpdir):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run({})
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199103.nc",
        "dst": str(tmpdir) + "/test.nc",
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


def test_ice_map_wrong_varname(tmpdir, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run({})
    assert "Invalid varname " in caplog.text


def test_ice_map_wrong_hemisphere(tmpdir, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_map = Si3HemisPointMonthMeanAllMeanMap(args)
    ice_map.run({})
    assert "Invalid hemisphere " in caplog.text
