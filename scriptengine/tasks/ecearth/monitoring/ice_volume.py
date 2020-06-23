"""Processing Task that calculates the global sea ice volume in one leg."""

import os
import warnings

import iris
import numpy as np
import cf_units

from scriptengine.tasks.base import Task
import helpers.file_handling as helpers

class SeaIceVolume(Task):
    """SeaIceVolume Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "domain",
            "dst",
            "hemisphere",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Sum of Sea-Ice Volume/**sivolu** in March and September"
                        f" on {self.hemisphere.title()}ern Hemisphere.")
        self.type = "time series"
        self.long_name = "Sea-Ice Volume"

    def run(self, context):
        """run function of SeaIceVolume Processing Task"""
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        domain = self.getarg('domain', context)
        hemisphere = self.getarg('hemisphere', context)
        self.log_info(f"Create sea ice volume time series for {hemisphere}ern hemisphere at {dst}.")
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

        leg_cube = helpers.load_input_cube([mar, sep], 'sivolu')
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
        leg_cube.standard_name = "sea_ice_volume"
        leg_cube.units = cf_units.Unit('m3')
        leg_cube.convert_units('1e3 km3')
        if hemisphere == "north":
            leg_cube.data = np.ma.masked_where(latitudes < 0, leg_cube.data)
            leg_cube.long_name = self.long_name + " North"
            leg_cube.var_name = "sivoln"
        elif hemisphere == "south":
            leg_cube.data = np.ma.masked_where(latitudes > 0, leg_cube.data)
            leg_cube.long_name = self.long_name + " South"
            leg_cube.var_name = "sivols"

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

    def save_cube(self, new_sivol, dst):
        """save sea ice volume cube in netCDF file"""
        try:
            current_sivol = iris.load_cube(dst)
            current_bounds = current_sivol.coord('time').bounds
            new_bounds = new_sivol.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                sivol_list = iris.cube.CubeList([current_sivol, new_sivol])
                sivol = sivol_list.concatenate_cube()
                iris.save(sivol, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save(new_sivol, dst)
        