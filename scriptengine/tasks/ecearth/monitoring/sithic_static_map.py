"""Processing Task that creates a 2D map of sea ice thickness."""

import os

import numpy as np
import iris
import iris_grib
import cftime
import datetime
import cf_units
from iris.experimental.equalise_cubes import equalise_attributes

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import render as j2render
import helpers.file_handling as helpers

class SithicStaticMap(Task):
    """SithicStaticMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "hemisphere",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Simulation Average of Sea-Ice Volume per Area/**sivolu** on {self.hemisphere.capitalize()}ern Hemisphere.")
        self.type = "static map"
        self.map_type = "polar ice sheet"
        self.long_name = "Sea-Ice Volume per Area"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        hemisphere = self.getarg('hemisphere', context)
        self.log_info(f"Create static sivolu map for {hemisphere}ern hemisphere at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        month_cube = iris.load_cube(src, 'sivolu')
        # Remove auxiliary time coordinate
        month_cube.remove_coord(month_cube.coord('time', dim_coords=False))
        month_cube = month_cube[0]
        month_cube.attributes.pop('uuid')
        month_cube.attributes.pop('timeStamp')
        time_coord = month_cube.coord('time')
        time_coord.bounds = self.get_time_bounds(time_coord)
        latitudes = np.broadcast_to(month_cube.coord('latitude').points, month_cube.shape)
        if hemisphere == "north":
            month_cube.data = np.ma.masked_where(latitudes < 0, month_cube.data)   
        elif hemisphere == "south":
            month_cube.data = np.ma.masked_where(latitudes > 0, month_cube.data)

        month_cube.long_name = f"{self.long_name} {hemisphere.capitalize()} {self.get_month(time_coord)}"
        month_cube.var_name = "sivol"
        month_cube.data = np.ma.masked_equal(month_cube.data, 0)

        month_cube.data = month_cube.data.astype('float64')
        month_cube = helpers.set_metadata(
            month_cube,
            title=f'{month_cube.long_name} (Climatology)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
            #presentation_min=0.0, # sithick can't be less than 0
        )
        time_coord.climatological = True
        month_cube.cell_methods = ()
        month_cube.add_cell_method(iris.coords.CellMethod('mean over years', coords='time'))
        month_cube.add_cell_method(iris.coords.CellMethod('point', coords='latitude', intervals=f'{hemisphere}ern hemisphere'))
        month_cube.add_cell_method(iris.coords.CellMethod('point', coords='longitude'))

        try:
            saved_diagnostic = iris.load_cube(dst)
        except OSError:
            iris.save(month_cube, dst)
        else:
            current_bounds = saved_diagnostic.coord('time').bounds
            new_bounds = month_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                saved_diagnostic.cell_methods = month_cube.cell_methods
                cube_list = iris.cube.CubeList([saved_diagnostic, month_cube])
                single_cube = cube_list.merge_cube()
                time_weights = self.compute_time_weights(single_cube, current_bounds)
                simulation_average = single_cube.collapsed(
                    'time',
                    iris.analysis.MEAN,
                    weights=time_weights,
                )
                iris.save(simulation_average, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)

    def compute_time_weights(self, cube, old_bounds):
        time_coord = cube.coord('time')
        old_dates = cftime.num2pydate(old_bounds[0], time_coord.units.name)
        old_start_year = int(old_dates[0].strftime("%Y"))
        old_end_year = int(old_dates[1].strftime("%Y"))
        time_weights = [old_end_year - old_start_year, 1]
        weight_shape = np.ones(cube[0].shape)
        time_weights = np.array([time_weight * weight_shape for time_weight in time_weights])
        return time_weights
    
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