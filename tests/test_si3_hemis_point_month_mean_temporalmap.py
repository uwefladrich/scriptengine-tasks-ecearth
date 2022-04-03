"""Tests for monitoring/si3_hemis_point_month_mean_temporalmap.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.si3_hemis_point_month_mean_temporalmap import (
    Si3HemisPointMonthMeanTemporalmap,
)


def test_si3_hemis_point_month_mean_temporalmap_once(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    ice_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "temporal map"


def test_si3_hemis_point_month_mean_temporalmap_twice(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    ice_time_map.run(init)
    init["src"] = "./tests/testdata/NEMO_output_sivolu-199103.nc",
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    ice_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "temporal map"


def test_si3_hemis_point_month_mean_temporalmap_wrong_varname(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        ice_time_map.run,
        init,
    )


def test_si3_hemis_point_month_mean_temporalmap_wrong_hemisphere(tmp_path):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmp_path / "test.nc"),
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        ice_time_map.run,
        init,
    )


# missing: 'convert_to' test (requires a siconc input file) or multiple Mocks
