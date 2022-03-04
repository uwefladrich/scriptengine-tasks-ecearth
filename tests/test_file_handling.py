"""Tests for files and cubes helpers"""

import os

import iris
import iris.cube
import numpy as np

import helpers.cubes
import helpers.nemo
from helpers.files import ChangeDirectory


def test_change_directory(tmpdir):
    cwd = os.getcwd()
    nwd = tmpdir.mkdir("temp")
    with ChangeDirectory(nwd):
        assert os.getcwd() == nwd
    assert os.getcwd() == cwd


def test_compute_spatial_weights(tmpdir):
    e1t_cube = iris.cube.Cube([1], var_name="e1t")
    e2t_cube = iris.cube.Cube([2], var_name="e2t")
    cube_list = iris.cube.CubeList([e1t_cube, e2t_cube])
    domain_path = str(tmpdir + "/temp.nc")
    iris.save(cube_list, domain_path)
    result = np.array([[[2]], [[2]], [[2]]])
    shape = result.shape
    assert (
        helpers.nemo.compute_spatial_weights(domain_path, shape, "T").all()
        == result.all()
    )


def test_load_input_cube():
    src = "./tests/testdata/tos_nemo_all_mean_map.nc"
    varname = "tos"
    assert isinstance(helpers.cubes.load_input_cube(src, varname), iris.cube.Cube)


def test_set_metadata():
    cube = iris.cube.Cube([1])
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
