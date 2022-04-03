"""Tests for monitoring/si3_hemis_point_month_mean_temporalmap.py"""

import iris
from iris.cube import Cube

from monitoring.si3_hemis_point_month_mean_temporalmap import (
    Si3HemisPointMonthMeanTemporalmap,
    _set_cell_methods,
)


def test_si3_hemis_point_month_mean_temporalmap_once(tmpdir):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(args)
    ice_time_map.run({})
    cube = iris.load_cube(args["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "temporal map"


def test_si3_hemis_point_month_mean_temporalmap_twice(tmpdir):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(args)
    ice_time_map.run({})
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199103.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(args)
    ice_time_map.run({})
    cube = iris.load_cube(args["dst"])
    assert cube.attributes["map_type"] == "polar ice sheet"
    assert cube.attributes["diagnostic_type"] == "temporal map"


def test_si3_hemis_point_month_mean_temporalmap_wrong_varname(tmpdir, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "north",
        "varname": "foo",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(args)
    ice_time_map.run({})
    assert "Invalid varname " in caplog.text


def test_si3_hemis_point_month_mean_temporalmap_wrong_hemisphere(tmpdir, caplog):
    args = {
        "src": "./tests/testdata/NEMO_output_sivolu-199003.nc",
        "dst": str(tmpdir) + "/test.nc",
        "hemisphere": "foo",
        "varname": "sivolu",
    }
    ice_time_map = Si3HemisPointMonthMeanTemporalmap(args)
    ice_time_map.run({})
    assert "Invalid hemisphere " in caplog.text


def test_set_cell_methods():
    cube = Cube([])
    assert cube.cell_methods == ()
    cube = _set_cell_methods(cube, "north")
    assert cube.cell_methods != ()


# missing: 'convert_to' test (requires a siconc input file) or multiple Mocks
