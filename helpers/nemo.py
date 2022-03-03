"""Helper module for NEMO data."""

import iris


def compute_spatial_weights(domain_src, array_shape, grid):
    "Compute weights for spatial averaging"
    domain_cfg = iris.load(domain_src)
    scale_factors = [
        domain_cfg.extract(f"e1{grid.lower()}")[0][0],
        domain_cfg.extract(f"e2{grid.lower()}")[0][0],
    ]
    cell_areas = scale_factors[0] * scale_factors[1]
    cell_weights = np.broadcast_to(cell_areas.data, array_shape)
    return cell_weights


def remove_unique_attributes(cube):
    # NEMO attributes unique to each file:
    cube.attributes.pop("uuid", None)
    cube.attributes.pop("timeStamp", None)
    return cube
