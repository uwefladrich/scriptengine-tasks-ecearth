"""Tests for Iris cubes helpers"""

import cf_units
import numpy as np
import pytest
from iris.coords import AuxCoord, DimCoord
from iris.cube import Cube
from iris.exceptions import CoordinateNotFoundError

import helpers.cubes


def test_load_input_cube():
    src = "./tests/testdata/tos_nemo_all_mean_map.nc"
    varname = "tos"
    assert isinstance(helpers.cubes.load_input_cube(src, varname), Cube)


def test_set_metadata():
    cube = Cube([1])
    cube.attributes = {
        "description": None,
        "interval_operation": None,
        "interval_write": None,
        "name": None,
        "online_operation": None,
    }
    updated_cube = helpers.cubes.set_metadata(cube)
    assert updated_cube.attributes == {"source": "EC-Earth 4", "Conventions": "CF-1.8"}
    new_metadata = {
        "title": "Title",
        "comment": "Comment",
        "diagnostic_type": "Type",
        "source": "EC-Earth 4",
        "Conventions": "CF-1.8",
        "custom": "Custom",
    }
    updated_cube = helpers.cubes.set_metadata(updated_cube, **new_metadata)
    assert updated_cube.attributes == new_metadata


def test_remove_aux_time():
    cube = Cube([1])
    cube.add_dim_coord(DimCoord([0], "time"), 0)

    # a cube without aux time coord remains unchanged
    prev_cube = cube.copy()
    cube = helpers.cubes.remove_aux_time(cube)
    assert prev_cube == cube

    # add an auxiliary time coord
    cube.add_aux_coord(AuxCoord([0], "time", long_name="time_points"))
    assert len(cube.coords("time")) == 2

    # aux time coord gets removed from a cube that has one
    cube = helpers.cubes.remove_aux_time(cube)
    assert len(cube.coords("time")) == 1
    pytest.raises(CoordinateNotFoundError, cube.coord, "time", dim_coords=False)


def test_extract_month():
    cube = Cube([0, 1, 2])
    day0 = cf_units.encode_time(1990, 3, 4, 0, 0, 0)
    day1 = cf_units.encode_time(1990, 3, 6, 0, 0, 0)
    day2 = cf_units.encode_time(1990, 4, 4, 0, 0, 0)
    time = DimCoord(
        [day0, day1, day2], "time", units="seconds since 1970-01-01 00:00:00"
    )
    cube.add_dim_coord(time, 0)
    cube = helpers.cubes.extract_month(cube, 3)
    assert cube.shape == (2,)


def test_mask_other_hemisphere():
    cube = Cube([0])
    cube.add_dim_coord(DimCoord([0], "latitude"), 0)
    hemisphere = "foo"
    pytest.raises(ValueError, helpers.cubes.mask_other_hemisphere, cube, hemisphere)

    src = "./tests/testdata/NEMO_output_sivolu-199003.nc"
    varname = "sivolu"
    cube = helpers.cubes.load_input_cube(src, varname)

    out_cube_ref = helpers.cubes.mask_other_hemisphere(cube, "north")
    hemisphere_vals = ["North", "n", "N"]
    for hemisphere in hemisphere_vals:
        out_cube = helpers.cubes.mask_other_hemisphere(cube, hemisphere)
        assert out_cube == out_cube_ref

    hemisphere_vals = ["South", "s", "S"]
    out_cube_ref = helpers.cubes.mask_other_hemisphere(cube, "south")
    for hemisphere in hemisphere_vals:
        out_cube = helpers.cubes.mask_other_hemisphere(cube, hemisphere)
        assert out_cube == out_cube_ref


def test_annual_time_bounds():
    cube = Cube([0])
    points = np.array([cf_units.encode_time(1990, 3, 4, 0, 0, 0)])
    bounds = np.array(
        [
            [
                cf_units.encode_time(1990, 3, 1, 0, 0, 0),
                cf_units.encode_time(1990, 4, 1, 0, 0, 0),
            ],
        ]
    )
    time = DimCoord(
        points, "time", units="seconds since 1970-01-01 00:00:00", bounds=bounds
    )
    cube.add_dim_coord(time, 0)
    cube = helpers.cubes.annual_time_bounds(cube)
    new_bounds = cube.coord("time").bounds
    annual_bounds = np.array(
        [
            [
                cf_units.encode_time(1990, 1, 1, 0, 0, 0),
                cf_units.encode_time(1991, 1, 1, 0, 0, 0),
            ],
        ]
    )
    assert (new_bounds == annual_bounds).all()
