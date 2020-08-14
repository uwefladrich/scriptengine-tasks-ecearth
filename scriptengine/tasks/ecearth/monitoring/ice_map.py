"""Processing Task that creates a 2D map of sea ice variables."""

import os

import numpy as np
import iris
import cftime
import datetime
import cf_units

from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import render as j2render
from .map import Map
import helpers.file_handling as helpers

meta_dict = {
    'sivolu': 'Sea-Ice Volume per Area',
    'siconc':'Sea-Ice Area Fraction',
}

class SeaIceMap(Map):
    """SeaIceMap Processing Task"""

    map_type = "polar ice sheet"

    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "hemisphere",
            "varname",
        ]
        super(Map, self).__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        hemisphere = self.getarg('hemisphere', context)
        varname = self.getarg('varname', context)
        self.log_info(f"Create static sivolu map for {hemisphere}ern hemisphere at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if varname not in meta_dict:
            self.log_error((
                f"'varname' must be one of the following: {meta_dict.keys()} "
                f"Diagnostic will not be treated, returning now."
            ))
            return
        if not hemisphere in ('north', 'south'):
            self.log_error((
                f"'hemisphere' must be 'north' or 'south' but is '{hemisphere}'."
                f"Diagnostic will not be treated, returning now."
            ))
        if not self.correct_file_extension(dst):
            return

        month_cube = helpers.load_input_cube(src, varname)
        # Remove auxiliary time coordinate
        month_cube.remove_coord(month_cube.coord('time', dim_coords=False))
        month_cube = month_cube[0]
        time_coord = month_cube.coord('time')
        time_coord.bounds = self.get_time_bounds(time_coord)
        latitudes = np.broadcast_to(month_cube.coord('latitude').points, month_cube.shape)
        if hemisphere == "north":
            month_cube.data = np.ma.masked_where(latitudes < 0, month_cube.data)   
        else:
            month_cube.data = np.ma.masked_where(latitudes > 0, month_cube.data)

        month_cube.long_name = f"{meta_dict[varname]} {hemisphere} {self.get_month(time_coord)}"
        month_cube.data = np.ma.masked_equal(month_cube.data, 0)

        month_cube.data = month_cube.data.astype('float64')
        comment = f"Simulation Average of {meta_dict[varname]} / **{varname}** on {hemisphere}ern hemisphere."
        month_cube = helpers.set_metadata(
            month_cube,
            title=f'{month_cube.long_name} (Climatology)',
            comment=comment,
            diagnostic_type=self.diagnostic_type,
            map_type=self.map_type,
        )
        time_coord.climatological = True
        month_cube.cell_methods = ()
        month_cube.add_cell_method(iris.coords.CellMethod('mean over years', coords='time'))
        month_cube.add_cell_method(iris.coords.CellMethod('point', coords='latitude', intervals=f'{hemisphere}ern hemisphere'))
        month_cube.add_cell_method(iris.coords.CellMethod('point', coords='longitude'))

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
        return dt_object.strftime('%B')