"""Processing Task that creates a 2D map of sea ice concentration."""

import os

import numpy as np
import iris
import iris_grib

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
import helpers.file_handling as helpers

class SeaIceMap(Task):
    """AtmosphereMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Maps of Sea Ice Concentration.")
        self.type = "map"
        self.map_type = "polar ice sheet"
        self.long_name = "Sea Ice Concentration"

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return
        
        try:
            mar = helpers.get_month_from_src("03", src)
            sep = helpers.get_month_from_src("09", src)
        except FileNotFoundError as error:
            self.log_warning((f"FileNotFoundError: {error}."
                              f"Diagnostic can not be created, returning now."))
            return

        leg_cube = helpers.load_input_cube([mar, sep], 'siconc')
        leg_cube.data = np.ma.masked_equal(leg_cube.data, 0) # mask land cells

        # Remove auxiliary time coordinate
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))

        nh_cube = leg_cube.copy()
        sh_cube = leg_cube.copy()
        latitudes = np.broadcast_to(leg_cube.coord('latitude').points, leg_cube.shape)
        nh_cube.data = np.ma.masked_where(latitudes < 0, leg_cube.data)
        sh_cube.data = np.ma.masked_where(latitudes > 0, leg_cube.data)
        nh_cube.long_name = self.long_name + " Northern Hemisphere"
        sh_cube.long_name = self.long_name + " Southern Hemisphere"
        nh_cube.var_name = 'siconcn'
        sh_cube.var_name = 'siconcs'

        nh_cube = helpers.set_metadata(
            nh_cube,
            title=f'{leg_cube.long_name} (Yearly Average Map)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )
        sh_cube = helpers.set_metadata(
            sh_cube,
            title=f'{leg_cube.long_name} (Yearly Average Map)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )

        self.save_cubes(nh_cube, sh_cube, dst)

    def save_cubes(self, new_nh_cube, new_sh_cube, dst):
        """save global average cubes in netCDF file"""
        try:
            current_nh_cube = iris.load_cube(dst, 'siconcn')
            current_sh_cube = iris.load_cube(dst, 'siconcs')
            current_bounds = current_nh_cube.coord('time').bounds
            new_bounds = new_nh_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                nh_cube_list = iris.cube.CubeList([current_nh_cube, new_nh_cube])
                sh_cube_list = iris.cube.CubeList([current_sh_cube, new_sh_cube])
                nh_cube = nh_cube_list.concatenate_cube()
                sh_cube = sh_cube_list.concatenate_cube()
                iris.save([nh_cube, sh_cube], f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save([new_nh_cube, new_sh_cube], dst)
            return
