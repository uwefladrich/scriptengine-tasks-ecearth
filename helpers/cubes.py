"""Helper module for Iris cubes."""

import warnings

import iris
import numpy as np
from iris.util import equalise_attributes
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError

from helpers.dates import month_number
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


def set_metadata(cube, **kwargs):
    """Set metadata for diagnostic."""
    defaults = {
        "source": "EC-Earth 4",
        "Conventions": "CF-1.8",
    }
    drop = (
        "description",
        "interval_operation",
        "interval_write",
        "name",
        "online_operation",
    )
    cube.attributes.update(dict(defaults, **kwargs))
    for key in drop:
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


def extract_month(cube, month):
    return cube.extract(
        iris.Constraint(time=lambda cell: cell.point.month == month_number(month))
    )


def remove_aux_time(cube):
    try:
        aux_time = cube.coord("time", dim_coords=False)
    except iris.exceptions.CoordinateNotFoundError:
        pass
    else:
        cube.remove_coord(aux_time)
    return cube


def annual_time_bounds(cube):

    t_coord = cube.coord("time")
    cube.remove_coord("time")

    t_point = t_coord.units.num2date(t_coord.points[0])
    t_first, t_last = (
        t_coord.units.date2num(t_point.replace(month=1, day=1)),
        t_coord.units.date2num(t_point.replace(year=t_point.year + 1, month=1, day=1)),
    )
    cube.add_aux_coord(
        iris.coords.DimCoord(
            t_coord.points,
            bounds=np.array([[t_first, t_last]]),
            standard_name=t_coord.standard_name,
            long_name=t_coord.long_name,
            units=t_coord.units,
            var_name=t_coord.var_name,
            attributes=t_coord.attributes,
        )
    )
    return iris.util.new_axis(cube, "time")


def mask_other_hemisphere(cube, hemisphere):
    lats = np.broadcast_to(cube.coord("latitude").points, cube.shape)
    if hemisphere.lower() in ("south", "s"):
        cube.data = np.ma.masked_where(lats > 0, cube.data)
    elif hemisphere.lower() in ("north", "n"):
        cube.data = np.ma.masked_where(lats < 0, cube.data)
    else:
        raise ValueError("Invalid hemisphere, must be 'north' or 'south'")
    return cube
