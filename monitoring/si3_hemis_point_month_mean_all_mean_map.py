"""Processing Task that creates a 2D map of sea ice variables."""

import datetime

import cftime
import iris
import numpy as np
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .map import Map

_meta_dict = {
    "sivolu": "Sea-Ice Volume per Area",
    "siconc": "Sea-Ice Area Fraction",
}


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
        dst = self.getarg("dst", context)
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
        if not hemisphere in ("north", "south"):
            self.log_warning(
                (
                    f"Invalid hemisphere '{hemisphere}', must be 'north' or 'south'; "
                    "diagnostic will not be ignored."
                )
            )
            return
        self.check_file_extension(dst)

        month_cube = helpers.cubes.load_input_cube(src, varname)
        # Remove auxiliary time coordinate
        month_cube.remove_coord(month_cube.coord("time", dim_coords=False))
        month_cube = month_cube[0]
        time_coord = month_cube.coord("time")
        time_coord.bounds = self.get_time_bounds(time_coord)
        latitudes = np.broadcast_to(
            month_cube.coord("latitude").points, month_cube.shape
        )
        if hemisphere == "north":
            month_cube.data = np.ma.masked_where(latitudes < 0, month_cube.data)
        else:
            month_cube.data = np.ma.masked_where(latitudes > 0, month_cube.data)

        month_cube.long_name = (
            f"{_meta_dict[varname]} {hemisphere} {self.get_month(time_coord)}"
        )
        month_cube.data = np.ma.masked_equal(month_cube.data, 0)

        month_cube.data = month_cube.data.astype("float64")
        comment = f"Simulation Average of {_meta_dict[varname]} / **{varname}** on {hemisphere}ern hemisphere."
        month_cube = helpers.cubes.set_metadata(
            month_cube,
            title=f"{month_cube.long_name} (Climatology)",
            comment=comment,
            map_type="polar ice sheet",
        )
        time_coord.climatological = True
        month_cube = self.set_cell_methods(month_cube, hemisphere)

        self.save(month_cube, dst)

    def get_time_bounds(self, time_coord):
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

    def get_month(self, time_coord):
        """
        Returns the month of [0] in time_coord.points as a string
        """
        dt_object = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
        return dt_object.strftime("%B")

    def set_cell_methods(self, cube, hemisphere):
        """Set the correct cell methods."""
        self.log_debug("Setting cell methods.")
        cube.cell_methods = ()
        cube.add_cell_method(iris.coords.CellMethod("mean over years", coords="time"))
        cube.add_cell_method(
            iris.coords.CellMethod(
                "point", coords="latitude", intervals=f"{hemisphere}ern hemisphere"
            )
        )
        cube.add_cell_method(iris.coords.CellMethod("point", coords="longitude"))
        return cube
