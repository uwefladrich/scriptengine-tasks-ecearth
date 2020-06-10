"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import os

import numpy as np
import iris

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
import helpers.file_handling as helpers

class OceanMap(Task):
    """OceanMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Map of **{self.varname}**.")
        self.type = "map"
        self.map_type = "global ocean"

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        varname = self.getarg('varname', context)

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        leg_cube = helpers.load_input_cube(src, varname)
        leg_cube.data = np.ma.masked_equal(leg_cube.data, 0) # mask land cells

        #month_weights = helpers.compute_month_weights(leg_cube, leg_cube.shape)
        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))
        ann_spatial_avg = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
        )
            #weights=month_weights)
        
        # Promote time from scalar to dimension coordinate
        ann_spatial_avg = iris.util.new_axis(ann_spatial_avg, 'time')
        #ann_spatial_avg = ann_spatial_avg[0]

        ann_spatial_avg = helpers.set_metadata(
            ann_spatial_avg,
            title=f'{ann_spatial_avg.long_name} (Yearly Average Map)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )
        self.save_cube(ann_spatial_avg, varname, dst)

    def save_cube(self, new_cube, varname, dst):
        """save global average cubes in netCDF file"""
        try:
            current_cube = iris.load_cube(dst, varname)
            current_bounds = current_cube.coord('time').bounds
            new_bounds = new_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                cube_list = iris.cube.CubeList([current_cube, new_cube])
                merged_cube = cube_list.concatenate_cube()
                iris.save(merged_cube, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return
        