"""Tests for files and cubes helpers"""

import os

import iris
import numpy as np
from iris.coords import DimCoord
from iris.cube import Cube, CubeList

import helpers.cubes
import helpers.nemo
from helpers.files import ChangeDirectory


def test_change_directory(tmpdir):
    cwd = os.getcwd()
    nwd = tmpdir.mkdir("temp")
    with ChangeDirectory(nwd):
        assert os.getcwd() == nwd
    assert os.getcwd() == cwd


def test_2d_spatial_weights(tmp_path):
    data = Cube(
        [[1.0]],
        var_name="foo",
        dim_coords_and_dims=[
            (DimCoord([0], standard_name="latitude", units="degree"), 0),
            (DimCoord([0], standard_name="longitude", units="degree"), 1),
        ],
    )
    domain = CubeList(
        [
            Cube([2.0], var_name="e1t"),
            Cube([3.0], var_name="e2t"),
        ]
    )
    domain_file = str(tmp_path / "domain.nc")
    iris.save(domain, domain_file)
    expected_weights = np.array([6.0])
    assert helpers.nemo.spatial_weights(data, domain_file, "t") == expected_weights


def test_3d_spatial_weights(tmp_path):
    data = Cube(
        [[[1.0]]],
        var_name="foo",
        dim_coords_and_dims=[
            (DimCoord([0], standard_name="latitude", units="degree"), 0),
            (DimCoord([0], standard_name="longitude", units="degree"), 1),
            (
                DimCoord(
                    [0], var_name="deptht", long_name="Vertical T levels", units="m"
                ),
                2,
            ),
        ],
    )
    domain = CubeList(
        [
            Cube([2.0], var_name="e1t"),
            Cube([3.0], var_name="e2t"),
            Cube([4.0], var_name="e3t_0"),
        ]
    )
    domain_file = str(tmp_path / "domain.nc")
    iris.save(domain, domain_file)
    expected_weights = np.array([24.0])
    assert helpers.nemo.spatial_weights(data, domain_file, "t") == expected_weights


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
