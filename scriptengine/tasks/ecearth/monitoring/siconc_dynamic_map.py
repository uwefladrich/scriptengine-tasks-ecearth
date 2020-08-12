"""Processing Task that creates a 2D dynamic map of sea ice concentration."""

import os
import datetime

import numpy as np
import iris
import cftime

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers

class SiconcDynamicMap(Task):
    """SiconcDynamicMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "hemisphere",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Dynamic Map of Sea Ice Concentration on {self.hemisphere.capitalize()}ern Hemisphere.") #TODO
        self.type = "dynamic map"
        self.map_type = "polar ice sheet"
        self.long_name = "Sea-Ice Area Fraction"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        hemisphere = self.getarg('hemisphere', context)
        self.log_info(f"Create dynamic siconc map for {hemisphere}ern hemisphere at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not hemisphere in ('north', 'south'):
            self.log_error((
                f"'hemisphere' must be 'north' or 'south' but is '{hemisphere}'."
                f"Diagnostic will not be treated, returning now."
            ))
        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        month_cube = helpers.load_input_cube(src, 'siconc')
        # Remove auxiliary time coordinate
        month_cube.remove_coord(month_cube.coord('time', dim_coords=False))
        time_coord = month_cube.coord('time')
        time_coord.bounds = self.get_time_bounds(time_coord)
        latitudes = np.broadcast_to(month_cube.coord('latitude').points, month_cube.shape)
        if hemisphere == "north":
            month_cube.data = np.ma.masked_where(latitudes < 0, month_cube.data)
        else:
            month_cube.data = np.ma.masked_where(latitudes > 0, month_cube.data)
        month_cube.long_name = f"{self.long_name} {hemisphere.capitalize()} {self.get_month(time_coord)}" #TODO
        month_cube.data = np.ma.masked_equal(month_cube.data, 0)
        month_cube.convert_units('%')

        month_cube = helpers.set_metadata(
            month_cube,
            title=f'{month_cube.long_name}',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
            presentation_min=0,
            presentation_max=100,
        )
        month_cube.cell_methods = ()
        month_cube.add_cell_method(iris.coords.CellMethod('point', coords='time'))
        month_cube.add_cell_method(iris.coords.CellMethod(
                'point',
                coords='latitude',
                comments=f'{hemisphere}ern hemisphere',
                ))
        month_cube.add_cell_method(iris.coords.CellMethod('point', coords='longitude'))

        try:
            saved_diagnostic = iris.load_cube(dst)
        except OSError: # file does not exist yet
            iris.save(month_cube, dst)
        else:
            current_bounds = saved_diagnostic.coord('time').bounds
            new_bounds = month_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                cube_list = iris.cube.CubeList([saved_diagnostic, month_cube])
                single_cube = cube_list.concatenate_cube()
                iris.save(single_cube, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)

    def get_time_bounds(self, time_coord):
        """
        Get contiguous time bounds for sea ice maps

        Creates new time bounds [
            [01-01-current year, 01-01-next year],
        ]
        """
        dt_object = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
        start = datetime.datetime(
            year=dt_object.year,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        end = datetime.datetime(
            year=start.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        start_seconds = cftime.date2num(start, time_coord.units.name)
        end_seconds = cftime.date2num(end, time_coord.units.name)
        new_bounds = np.array([[start_seconds, end_seconds]])
        return new_bounds

    def get_month(self, time_coord):
        """
        Returns the month of [0] in time_coord.points as a string
        """
        dt_object = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
        return dt_object.strftime('%B')
