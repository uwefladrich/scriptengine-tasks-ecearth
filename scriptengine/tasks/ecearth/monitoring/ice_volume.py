"""Processing Task that calculates the global sea ice volume in one leg."""

import os
import ast

import iris
import numpy as np
import cf_units

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
import helpers.file_handling as helpers

class SeaIceVolume(Task):
    """SeaIceVolume Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "domain",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global Ice Volume over one leg, "
                        f"separated into Northern and Southern Hemisphere. ")
        self.type = "time series"
        self.long_name = "Global Sea Ice Volume"

    def run(self, context):
        """run function of SeaIceVolume Processing Task"""
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        domain = self.getarg('domain', context)
        #try:
        #    src = ast.literal_eval(src)
        #except ValueError:
        #    src = ast.literal_eval(f'"{src}"')

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
            title=self.long_name.title(),
            comment=self.comment,
            diagnostic_type=self.type,
        )
        leg_cube.standard_name = "sea_ice_volume"
        leg_cube.units = cf_units.Unit('m3')
        leg_cube.convert_units('1e3 km3')

        nh_cube = leg_cube.copy()
        sh_cube = leg_cube.copy()
        nh_cube.data = np.ma.masked_where(latitudes < 0, leg_cube.data)
        sh_cube.data = np.ma.masked_where(latitudes > 0, leg_cube.data)

        nh_weighted_sum = nh_cube.collapsed(
            ['latitude', 'longitude'],
            iris.analysis.SUM,
            weights=cell_weights,
            )
        sh_weighted_sum = sh_cube.collapsed(
            ['latitude', 'longitude'],
            iris.analysis.SUM,
            weights=cell_weights,
            )
        nh_weighted_sum.long_name = self.long_name + " on Northern Hemisphere"
        sh_weighted_sum.long_name = self.long_name + " on Southern Hemisphere"
        nh_weighted_sum.var_name = 'sivoln'
        sh_weighted_sum.var_name = 'sivols'

        self.save_cubes(nh_weighted_sum, sh_weighted_sum, dst)

    def save_cubes(self, new_sivoln, new_sivols, dst):
        """save sea ice volume cubes in netCDF file"""
        try:
            current_sivoln = iris.load_cube(dst, 'sivoln')
            current_sivols = iris.load_cube(dst, 'sivols')
            current_bounds = current_sivoln.coord('time').bounds
            new_bounds = new_sivoln.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                sivoln_list = iris.cube.CubeList([current_sivoln, new_sivoln])
                sivols_list = iris.cube.CubeList([current_sivols, new_sivols])
                sivoln = sivoln_list.concatenate_cube()
                sivols = sivols_list.concatenate_cube()
                sivol_global = iris.cube.CubeList([sivoln, sivols])
                iris.save(sivol_global, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            sivol_global = iris.cube.CubeList([new_sivoln, new_sivols])
            iris.save(sivol_global, dst)
        