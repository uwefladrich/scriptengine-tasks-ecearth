"""Tests for monitoring/map.py"""
from pathlib import Path

import iris
import pytest
import scriptengine.exceptions

from monitoring.map import Map


def test_map_dst_error():
    test_map = Map({})
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskArgumentInvalidError,
        test_map.check_file_extension,
        Path("test.yml"),
    )


def test_map_nonmonotonic_increase(tmp_path):
    test_map = Map({})

    old_coord_with_bounds = iris.coords.DimCoord(
        [1], bounds=[0.5, 1.5], var_name="time"
    )
    new_coord_with_bounds = iris.coords.DimCoord(
        [2], bounds=[1.5, 2.5], var_name="time"
    )
    old_cube = iris.cube.Cube([0], dim_coords_and_dims=[(old_coord_with_bounds, 0)])
    new_cube = iris.cube.Cube([0], dim_coords_and_dims=[(new_coord_with_bounds, 0)])
    out_path = str(tmp_path / "new_cube.nc")
    iris.save(new_cube, out_path)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        test_map.save,
        old_cube,
        out_path,
    )
