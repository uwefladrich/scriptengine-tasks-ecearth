"""Helper module for handling files."""

import os
import warnings

import iris
import numpy as np
from iris.util import equalise_attributes
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError


# Using https://stackoverflow.com/revisions/13197763/9
class ChangeDirectory:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def spatial_coord_names(cube):
    """Returns the names of all cube coordinates that are listed as 'spatial' coordinates"""
    for cname in (c.name() for c in cube.coords()):
        if cname in (
            "latitude",
            "longitude",
            "Vertical T levels",
            "Vertical U levels",
            "Vertical V levels",
        ):
            yield cname


def spatial_weights(cube, domain_fname, grid="t"):
    """Compute weights for spatial averaging"""
    volume = len(cube.shape) == 4
    domain = iris.load(domain_fname)
    e1, e2 = (
        domain.extract(f"e1{grid.lower()}")[0][0],
        domain.extract(f"e2{grid.lower()}")[0][0],
    )
    if volume:
        e3 = domain.extract(f"e3{grid.lower()}_0")[0][0]
    weights = e1 * e2 * e3 if volume else e1 * e2
    return np.broadcast_to(weights.data, cube.shape)


def compute_time_weights(monthly_data_cube, cube_shape=None):
    """Compute weights for the different month lengths"""
    time_dim = monthly_data_cube.coord("time", dim_coords=True)
    month_weights = np.array([bound[1] - bound[0] for bound in time_dim.bounds])
    if cube_shape:
        weight_shape = np.ones(cube_shape[1:])
        month_weights = np.array(
            [time_weight * weight_shape for time_weight in month_weights]
        )
    return month_weights


def load_input_cube(src, varname):
    """Load input file(s) into one cube."""
    with warnings.catch_warnings():
        # Suppress psu warning
        warnings.filterwarnings(
            action="ignore",
            message="Ignoring netCDF variable",
            category=UserWarning,
        )
        month_cubes = iris.load(src, varname)
    if len(month_cubes) == 0:
        raise ScriptEngineTaskArgumentInvalidError(
            f"varname {varname} not found in {src}"
        )
    if len(month_cubes) == 1:
        month_cube = remove_unique_attributes(month_cubes[0])
        return month_cube
    equalise_attributes(
        month_cubes
    )  # 'timeStamp' and 'uuid' would cause ConcatenateError
    leg_cube = month_cubes.concatenate_cube()
    return leg_cube


def set_metadata(cube, title=None, comment=None, **kwargs):
    """Set metadata for diagnostic."""
    metadata = {
        "title": title,
        "comment": comment,
        "source": "EC-Earth 4",
        "Conventions": "CF-1.8",
    }
    for key, value in kwargs.items():
        metadata[f"{key}"] = value

    metadata_to_discard = [
        "description",
        "interval_operation",
        "interval_write",
        "name",
        "online_operation",
    ]
    for key, value in metadata.items():
        if value is not None:
            cube.attributes[key] = value
    for key in metadata_to_discard:
        cube.attributes.pop(key, None)
    return cube


def remove_unique_attributes(cube):
    # NEMO attributes unique to each file:
    cube.attributes.pop("uuid", None)
    cube.attributes.pop("timeStamp", None)
    return cube
