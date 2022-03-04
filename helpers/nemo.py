"""Helper module for NEMO data."""

import iris
import numpy as np

_nemo_horizontal_coords = (
    "latitude",
    "longitude",
)

_nemo_vertical_coords = (
    "Vertical T levels",
    "Vertical U levels",
    "Vertical V levels",
)


def spatial_coords(cube):
    """Returns the names of all cube coordinates that are listed as 'spatial' coordinates"""
    for cname in (c.name() for c in cube.coords()):
        if cname in (*_nemo_horizontal_coords, *_nemo_vertical_coords):
            yield cname


def _has_vertical_coord(cube):
    return not set(spatial_coords(cube)).isdisjoint(set(_nemo_vertical_coords))


def spatial_weights(cube, domain_file, grid):
    """Compute cell weights for spatial averaging in 2d and 3d"""
    domain = iris.load(domain_file)
    e1, e2 = (  # NEMO grid scale factors in horizontal directions
        domain.extract(f"e1{grid.lower()}")[0][0],
        domain.extract(f"e2{grid.lower()}")[0][0],
    )
    is_3d = _has_vertical_coord(cube)
    if is_3d:
        e3 = domain.extract(f"e3{grid.lower()}_0")[0][0]
    weights = e1 * e2 * e3 if is_3d else e1 * e2
    return np.broadcast_to(weights.data, cube.shape)


def remove_unique_attributes(cube):
    drop = ("uuid", "timeStamp")  # these are unique for each NEMO file
    for attribute in drop:
        cube.attributes.pop(attribute, None)
    return cube
