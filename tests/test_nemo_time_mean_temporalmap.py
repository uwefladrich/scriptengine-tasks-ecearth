"""Tests for monitoring/nemo_time_mean_temporalmap.py"""

import iris
import pytest

from monitoring.nemo_time_mean_temporalmap import (
    NemoMonthMeanTemporalmap,
    NemoTimeMeanTemporalmap,
    NemoYearMeanTemporalmap,
)


def test_nemo_time_mean_temporalmap_base(tmp_path):
    init = {
        "src": [
            "./tests/testdata/NEMO_output_sivolu-199003.nc",
            "./tests/testdata/NEMO_output_sivolu-199009.nc",
        ],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_time_map = NemoTimeMeanTemporalmap(init)
    with pytest.raises(NotImplementedError):
        ocean_time_map.run(init)


def test_nemo_year_mean_temporalmap_once(tmp_path):
    init = {
        "src": [
            "./tests/testdata/NEMO_output_sivolu-199003.nc",
            "./tests/testdata/NEMO_output_sivolu-199009.nc",
        ],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_time_map = NemoYearMeanTemporalmap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "global ocean"
    assert cube.attributes["diagnostic_type"] == "temporal map"
    assert cube.data.shape[0] == 1


def test_nemo_year_mean_temporalmap_twice(tmp_path):
    init = {
        "src": ["./tests/testdata/NEMO_output_sivolu-199003.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_time_map = NemoYearMeanTemporalmap(init)
    ocean_time_map.run(init)
    init["src"] = ["./tests/testdata/NEMO_output_sivolu-199009.nc"]
    ocean_time_map = NemoYearMeanTemporalmap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "global ocean"
    assert cube.attributes["diagnostic_type"] == "temporal map"
    assert cube.data.shape[0] == 2


def test_nemo_month_mean_temporalmap_once(tmp_path):
    init = {
        "src": [
            "./tests/testdata/NEMO_output_sivolu-199003.nc",
            "./tests/testdata/NEMO_output_sivolu-199009.nc",
        ],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_time_map = NemoMonthMeanTemporalmap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "global ocean"
    assert cube.attributes["diagnostic_type"] == "temporal map"
    assert cube.data.shape[0] == len(init["src"])


def test_nemo_month_mean_temporalmap_twice(tmp_path):
    init = {
        "src": ["./tests/testdata/NEMO_output_sivolu-199003.nc"],
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
    }
    ocean_time_map = NemoMonthMeanTemporalmap(init)
    ocean_time_map.run(init)
    init["src"] = ["./tests/testdata/NEMO_output_sivolu-199009.nc"]
    ocean_time_map = NemoMonthMeanTemporalmap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "global ocean"
    assert cube.attributes["diagnostic_type"] == "temporal map"
    assert cube.data.shape[0] == 2
