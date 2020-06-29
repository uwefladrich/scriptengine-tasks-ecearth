"""Processing Task that calculates the global sea ice area in one leg."""

import os
import warnings

import iris
import numpy as np
import cf_units
import cftime
import datetime

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers

class SeaIceArea(Task):
    """SeaIceArea Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "domain",
            "dst",
            "hemisphere",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Sum of Sea-Ice Area/**siconc** in March and September"
                        f" on {self.hemisphere.title()}ern Hemisphere.")
        self.type = "time series"
        self.long_name = "Sea-Ice Area"

    @timed_runner
    def run(self, context):
        """run function of SeaIceArea Processing Task"""
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        domain = self.getarg('domain', context)
        hemisphere = self.getarg('hemisphere', context)
        self.log_info(f"Create sea ice area time series for {hemisphere}ern hemisphere at {dst}.")
        self.log_debug(f"Domain: {domain}, Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic can not be saved, returning now."
            ))
            return

        # Get March and September files from src
        try:
            mar = helpers.get_month_from_src("03", src)
            sep = helpers.get_month_from_src("09", src)
        except FileNotFoundError as error:
            self.log_warning((f"FileNotFoundError: {error}."
                              f"Diagnostic can not be created, returning now."))
            return

        leg_cube = helpers.load_input_cube([mar, sep], 'siconc')
        latitudes = np.broadcast_to(leg_cube.coord('latitude').points, leg_cube.shape)
        cell_weights = helpers.compute_spatial_weights(domain, leg_cube.shape)

        # Treat main cube properties before extracting hemispheres
        # Remove auxiliary time coordinate
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))
        leg_cube = helpers.set_metadata(
            leg_cube,
            title=f"{self.long_name} {self.type.title()}",
            comment=self.comment,
            diagnostic_type=self.type,
        )
        leg_cube.standard_name = "sea_ice_area"
        leg_cube.units = cf_units.Unit('m2')
        leg_cube.convert_units('1e6 km2')
        if hemisphere == "north":
            leg_cube.data = np.ma.masked_where(latitudes < 0, leg_cube.data)
            leg_cube.long_name = self.long_name + " North"
            leg_cube.var_name = "siarean"
        elif hemisphere == "south":
            leg_cube.data = np.ma.masked_where(latitudes > 0, leg_cube.data)
            leg_cube.long_name = self.long_name + " South"
            leg_cube.var_name = "siareas"

        time_coord = leg_cube.coord('time')
        time_coord.bounds = self.get_time_bounds(time_coord)

        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                'ignore',
                "Collapsing a multi-dimensional coordinate.",
                UserWarning,
                )
            hemispheric_weighted_sum = leg_cube.collapsed(
                ['latitude', 'longitude'],
                iris.analysis.SUM,
                weights=cell_weights,
                )

        self.save_cube(hemispheric_weighted_sum, dst)

    def save_cube(self, new_siarea, dst):
        """save sea ice area cube in netCDF file"""
        try:
            current_siarea = iris.load_cube(dst)
            current_bounds = current_siarea.coord('time').bounds
            new_bounds = new_siarea.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                siarea_list = iris.cube.CubeList([current_siarea, new_siarea])
                siarea = siarea_list.concatenate_cube()
                iris.save(siarea, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save(new_siarea, dst)
    
    def get_time_bounds(self, time_coord):
        """
        Get contiguous time bounds for sea ice time series

        Creates new time bounds [
            [01-01-current year, 01-07-current year],
            [01-07-current year, 01-01-next year],
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
        mid_of_year = datetime.datetime(
            year=dt_object.year,
            month=7,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        start_seconds = cftime.date2num(start, time_coord.units.name)
        end_seconds = cftime.date2num(end, time_coord.units.name)
        mid_of_year_seconds = cftime.date2num(mid_of_year, time_coord.units.name)
        new_bounds = np.array([
            [start_seconds, mid_of_year_seconds],
            [mid_of_year_seconds, end_seconds],
        ])
        return new_bounds
