"""Processing Task that creates a 2D map of sea ice variables."""
import datetime
from pathlib import Path

import cftime
import iris
import numpy as np
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .map import Map

_meta_dict = {
    "sivolu": "Sea-Ice Volume per Area",
    "siconc": "Sea-Ice Area Fraction",
}


def _get_time_bounds(time_coord):
    """
    Get contiguous time bounds for sea ice maps

    Creates new time bounds [
        [01-01-current year, 01-01-next year],
    ]
    """
    dt_object = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
    start = datetime.datetime(dt_object.year, 1, 1)
    end = datetime.datetime(start.year + 1, 1, 1)
    start_seconds = cftime.date2num(start, time_coord.units.name)
    end_seconds = cftime.date2num(end, time_coord.units.name)
    new_bounds = np.array([[start_seconds, end_seconds]])
    return new_bounds


def _get_month(time_coord):
    """
    Returns the month of [0] in time_coord.points as a string
    """
    dt_object = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
    return dt_object.strftime("%B")


def _set_cell_methods(cube, hemisphere):
    """Set the correct cell methods."""
    cube.cell_methods = (
        iris.coords.CellMethod("mean over years", coords="time"),
        iris.coords.CellMethod(
            "point", coords="latitude", intervals=f"{hemisphere}ern hemisphere"
        ),
        iris.coords.CellMethod("point", coords="longitude"),
    )
    return cube


class Si3HemisPointMonthMeanAllMeanMap(Map):
    """Si3HemisPointMonthMeanAllMeanMap Processing Task"""

    _required_arguments = (
        "src",
        "dst",
        "hemisphere",
        "varname",
    )

    def __init__(self, arguments=None):
        Si3HemisPointMonthMeanAllMeanMap.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = Path(self.getarg("dst", context))
        hemisphere = self.getarg("hemisphere", context)
        varname = self.getarg("varname", context)

        self.log_info(f"Map for {varname} ({hemisphere}ern hemisphere): {dst}")
        self.log_debug(f"Source file(s): {src}")

        if varname not in _meta_dict:
            self.log_warning(
                (
                    f"Invalid varname '{varname}', must be one of {_meta_dict.keys()}; "
                    "diagnostic will not be ignored."
                )
            )
            return
        if hemisphere not in ("north", "south"):
            self.log_warning(
                (
                    f"Invalid hemisphere '{hemisphere}', must be 'north' or 'south'; "
                    "diagnostic will not be ignored."
                )
            )
            return
        self.check_file_extension(dst)

        month_cube = helpers.cubes.load_input_cube(src, varname)
        month_cube = helpers.cubes.remove_aux_time(month_cube)
        month_cube = month_cube[0]

        time_coord = month_cube.coord("time")
        time_coord.bounds = _get_time_bounds(time_coord)
        time_coord.climatological = True

        month_cube = helpers.cubes.mask_other_hemisphere(month_cube, hemisphere)
        month_cube.data = np.ma.masked_equal(month_cube.data, 0)
        month_cube.data = month_cube.data.astype("float64")

        month_cube.long_name = (
            f"{_meta_dict[varname]} {hemisphere} {_get_month(time_coord)}"
        )
        comment = f"Simulation Average of {_meta_dict[varname]} / **{varname}** on {hemisphere}ern hemisphere."
        month_cube = helpers.cubes.set_metadata(
            month_cube,
            title=f"{month_cube.long_name} (Climatology)",
            comment=comment,
            map_type="polar ice sheet",
        )

        month_cube = _set_cell_methods(month_cube, hemisphere)

        self.save(month_cube, dst)
