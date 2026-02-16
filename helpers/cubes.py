"""Helper module for Iris cubes."""

import warnings

import iris
import iris.analysis.cartography
import iris.cube
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


DEFAULT_UNIT_CONVERSIONS = {
    "kelvin": "degC",
    "meter^-2-kilogram-second^-1": "meter^-2-kilogram-day^-1",
}


def convert_units(cube: iris.cube.Cube, conversions=None) -> iris.cube.Cube:
    """Converts units of an Iris cube

    Converts units if the current unit is present in the 'conversions' dict.
    Does nothing otherwise.

    Args:
        cube: An Iris cube
        conversions: A mapping (dict) with 'unit': 'converted_unit' strings.
          If None (default), then DEFAULT_UNIT_CONVERSIONS (defined above) is used.
    Returns:
        An Iris cube with modified units.
    """
    if conversions is None:
        conversions = DEFAULT_UNIT_CONVERSIONS
    try:
        cube.convert_units(conversions[cube.units.name])
    except KeyError:
        pass
    return cube


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


def compute_annual_mean(cube):
    # Remove auxiliary time coordinate before collapsing cube
    try:
        cube.coord("time")
    except iris.exceptions.CoordinateNotFoundError:
        cube.remove_coord(cube.coord("time", dim_coords=False))

    annual_mean = cube.collapsed(
        "time",
        iris.analysis.MEAN,
        weights=compute_time_weights(cube),
    )
    # Promote time from scalar to dimension coordinate
    annual_mean = iris.util.new_axis(annual_mean, "time")
    return annual_mean


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


def compute_area_weights(cube):
    if is_grid_regular(cube):
        return compute_regular_grid_weights(cube)
    return compute_reduced_grid_weights(cube)


def is_grid_regular(cube) -> bool:
    if not cube.coords("latitude", dim_coords=True):
        return False
    return True


def compute_reduced_grid_weights(cube):
    """compute area weights for the reduced gaussian grid"""
    nh_latitudes = np.ma.masked_less(cube.coord("latitude").points, 0)
    unique_lats, gridpoints_per_lat = np.unique(nh_latitudes, return_counts=True)
    unique_lats, gridpoints_per_lat = unique_lats[0:-1], gridpoints_per_lat[0:-1]
    areas = []
    last_angle = 0
    earth_radius = 6371
    for latitude, amount in zip(unique_lats, gridpoints_per_lat):
        delta = latitude - last_angle
        current_angle = last_angle + 2 * delta
        sin_diff = np.sin(np.deg2rad(current_angle)) - np.sin(np.deg2rad(last_angle))
        ring_area = 2 * np.pi * earth_radius**2 * sin_diff
        grid_area = ring_area / amount
        areas.extend([grid_area] * amount)
        last_angle = current_angle
    areas = np.append(areas[::-1], areas)
    area_weights = np.broadcast_to(areas, cube.data.shape)
    return area_weights


def compute_regular_grid_weights(cube):
    """compute area weights for a regular lat/lon grid"""
    cube.coord("latitude").guess_bounds()
    cube.coord("longitude").guess_bounds()
    return iris.analysis.cartography.area_weights(cube)

def align_time_coords(new_cube, old_cube):
    """
    Align the time coordinates in two cubes. 
    Useful if one cube has time in units seconds since 1990-01-01 00:00:00
    while the other has seconds since 1995-01-01 00:00:00. 
    Iris can not concatenate two such cubes. 
    """
    # convert time coord in new cube to that of old cube
    new_cube.coord("time").convert_units(old_cube.coord("time").units)

    # We also need to match the attribute time_origin between
    # new_cube and current_cube to make Iris happy.
    # Note: This does not always exist
    if (     "time_origin" in old_cube.coord("time").attributes.keys()
         and "time_origin" in new_cube.coord("time").attributes.keys() ):
        new_cube.coord("time").attributes["time_origin"] = old_cube.coord("time").attributes["time_origin"]
    elif ( "time_origin" in     old_cube.coord("time").attributes.keys() and 
           "time_origin" not in new_cube.coord("time").attributes.keys() ):
        raise ScriptEngineTaskRunError("Attribute time_origin for time coord exists in old_cube but not new_cube")
    elif ( "time_origin" not in old_cube.coord("time").attributes.keys() and
           "time_origin" in     new_cube.coord("time").attributes.keys() ):
        raise ScriptEngineTaskRunError("Attribute time_origin for time coord exists in new_cube but not old_cube")
    return new_cube
