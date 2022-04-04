"""Tests for monitoring/nemo_all_mean_map.py"""

import iris

from monitoring.nemo_all_mean_map import NemoAllMeanMap


def test_nemo_all_mean_map_once(tmp_path):
    init = {
        "src": [
            "./tests/testdata/NEMO_output_sivolu-199003.nc",
            "./tests/testdata/NEMO_output_sivolu-199009.nc",
        ],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_map = NemoAllMeanMap(init)
    ocean_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "global ocean"
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1


def test_nemo_all_mean_map_twice(tmp_path):
    init = {
        "src": ["./tests/testdata/NEMO_output_sivolu-199003.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_map = NemoAllMeanMap(init)
    ocean_map.run(init)
    init["src"] = "./tests/testdata/NEMO_output_sivolu-199103.nc"
    ocean_map = NemoAllMeanMap(init)
    ocean_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "global ocean"
    assert cube.attributes["diagnostic_type"] == "map"
    assert cube.coord("time").climatological
    assert len(cube.coord("time").points) == 1
