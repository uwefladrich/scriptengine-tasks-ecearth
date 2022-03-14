"""Helper module for NEMO data."""

import iris
import numpy as np
from iris.exceptions import CoordinateNotFoundError

_nemo_horizontal_coords = (
    "latitude",
    "longitude",
)

_nemo_vertical_coords = (
    "deptht",
    "Vertical T levels",
    "depthu",
    "Vertical U levels",
    "depthv",
    "Vertical V levels",
)


def _yield_coords(cube, names):
    for c in cube.coords():
        if c.name() in names:
            yield c


def area_coords(cube):
    return _yield_coords(cube, _nemo_horizontal_coords)


def spatial_coords(cube):
    return _yield_coords(cube, (*_nemo_horizontal_coords, *_nemo_vertical_coords))


def depth_coords(cube):
    return _yield_coords(cube, _nemo_vertical_coords)


def depth_coord(cube):
    coords = tuple(depth_coords(cube))
    if len(coords) != 1:
        raise CoordinateNotFoundError(
            "More than one depth coordinate found in NEMO data"
            if len(coords)
            else "No depth coordinate found in NEMO data"
        )
    coord = coords[0]
    if not coord.standard_name:
        coord.standard_name = "depth"
    return coord


def has_depth(cube):
    return len(tuple(depth_coords(cube))) > 0


def spatial_weights(cube, domain_file, grid):
    """Compute cell weights for spatial averaging in 2d and 3d"""
    domain = iris.load(domain_file)
    e1, e2 = (  # NEMO grid scale factors in horizontal directions
        domain.extract(f"e1{grid.lower()}")[0][0],
        domain.extract(f"e2{grid.lower()}")[0][0],
    )
    is_3d = has_depth(cube)
    if is_3d:
        e3 = domain.extract(f"e3{grid.lower()}_0")[0][0]
    weights = e1 * e2 * e3 if is_3d else e1 * e2
    return np.broadcast_to(weights.data, cube.shape)


def remove_unique_attributes(cube):
    drop = ("uuid", "timeStamp")  # these are unique for each NEMO file
    for attribute in drop:
        cube.attributes.pop(attribute, None)
    return cube
