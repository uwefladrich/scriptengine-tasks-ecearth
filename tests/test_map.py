"""Tests for monitoring/map.py"""

import pytest
import iris

import scriptengine.exceptions
from monitoring.map import Map

def test_map_dst_error():
    test_map = Map({})
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        test_map.check_file_extension,
        'test.yml',
    )

def test_map_nonmonotonic_increase(tmpdir):
    test_map = Map({})

    old_coord_with_bounds = iris.coords.DimCoord([1], bounds=[0.5, 1.5], var_name='time')
    new_coord_with_bounds = iris.coords.DimCoord([2], bounds=[1.5, 2.5], var_name='time')
    old_cube = iris.cube.Cube([0], dim_coords_and_dims=[(old_coord_with_bounds, 0)])
    new_cube = iris.cube.Cube([0], dim_coords_and_dims=[(new_coord_with_bounds, 0)])
    iris.save(new_cube, str(tmpdir) + '/new_cube.nc')
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        test_map.save,
        old_cube,
        str(tmpdir) + '/new_cube.nc',
        )
