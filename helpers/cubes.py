"""Helper module for Iris cubes."""

import warnings

import iris
import numpy as np
from iris.util import equalise_attributes
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError

from helpers.nemo import remove_unique_attributes


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
