"""Tests for monitoring/si3_hemis_point_month_mean_temporalmap.py"""

import iris
import pytest
import scriptengine.exceptions

from monitoring.si3_hemis_point_month_mean_temporalmap import (
    Si3HemisPointMonthMeanTemporalmap,
)


def test_si3_hemis_point_month_mean_temporalmap_once(tmpdir):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    ice_time_map.run(init)
    cube = iris.load_cube(init["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "temporal map"


def test_si3_hemis_point_month_mean_temporalmap_twice(tmpdir):
    init_a = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init_a)
    ice_time_map.run(init_a)
    init_b = {
        "src": "./tests/testdata/NEMO_output_sivolu-199103.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init_b)
    ice_time_map.run(init_b)
    cube = iris.load_cube(init_b["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "temporal map"


def test_si3_hemis_point_month_mean_temporalmap_wrong_varname(tmpdir):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "tos",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        ice_time_map.run,
        init,
    )


def test_si3_hemis_point_month_mean_temporalmap_wrong_hemisphere(tmpdir):
    init = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
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
