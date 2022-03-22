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
