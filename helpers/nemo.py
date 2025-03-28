"""Helper module for NEMO data."""

import warnings

import iris
import numpy as np
from iris.analysis import WeightedAggregator
from iris.coords import CellMeasure
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


def _add_cell_size(cube, domain_file, grid):
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
    weights = np.broadcast_to(weights.data, cube.shape)
    if is_3d:
        cell_size = CellMeasure(
            weights, var_name="cell_size", units="m3", measure="volume"
        )
    else:
        cell_size = CellMeasure(
            weights, var_name="cell_size", units="m2", measure="area"
        )
    dims = tuple(range(len(weights.shape)))
    cube.add_cell_measure(cell_size, dims)


def remove_unique_attributes(cube):
    drop = ("uuid", "timeStamp")  # these are unique for each NEMO file
    for attribute in drop:
        cube.attributes.pop(attribute, None)
    return cube


def compute_global_aggregate(cube, domain, grid, operation: WeightedAggregator):
    _add_cell_size(cube, domain, grid)
    with warnings.catch_warnings():
        # Suppress warning about insufficient metadata.
        warnings.filterwarnings(
            "ignore",
            "Collapsing a multi-dimensional coordinate.",
            UserWarning,
        )
        global_aggregate = cube.collapsed(
            spatial_coords(cube),
            operation,
            weights="cell_size",
        )
    return global_aggregate
