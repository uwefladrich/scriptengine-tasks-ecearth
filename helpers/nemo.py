"""Helper module for NEMO data."""

import iris
import numpy as np


def spatial_weights(domain_file, array_shape, grid):
    "Compute weights for spatial averaging"
    domain = iris.load(domain_file)
    e1, e2 = (  # NEMO grid scale factors in horizontal directions
        domain.extract(f"e1{grid.lower()}")[0][0],
        domain.extract(f"e2{grid.lower()}")[0][0],
    )
    cell_areas = e1 * e2
    cell_weights = np.broadcast_to(cell_areas.data, array_shape)
    return cell_weights


def remove_unique_attributes(cube):
    drop = ("uuid", "timeStamp")  # these are unique for each NEMO file
    for attribute in drop:
        cube.attributes.pop(attribute, None)
    return cube
