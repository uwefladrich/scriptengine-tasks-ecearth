"""Processing Task that creates a 2D dynamic map of a given extensive ocean quantity."""

import os

import iris
import numpy as np

from scriptengine.tasks.base import Task
import helpers.file_handling as helpers

class OceanDynamicMap(Task):
    """OceanDynamicMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Annual Average Dynamic Map of **{self.varname}**.")
        self.type = "dynamic map"
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

        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))

        month_weights = helpers.compute_time_weights(leg_cube, leg_cube.shape)
        annual_avg = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=month_weights
        )

        # Promote time from scalar to dimension coordinate
        annual_avg = iris.util.new_axis(annual_avg, 'time')

        annual_avg = helpers.set_metadata(
            annual_avg,
            title=f'{annual_avg.long_name.title()} {self.type.title()}',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )
        self.save_cube(annual_avg, varname, dst)

    def save_cube(self, new_cube, varname, dst):
        """save global average cubes in netCDF file"""
        try:
            current_cube = iris.load_cube(dst, varname)
            current_bounds = current_cube.coord('time').bounds
            new_bounds = new_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                new_cube.attributes["presentation_min"] = current_cube.attributes["presentation_min"]
                new_cube.attributes["presentation_max"] = current_cube.attributes["presentation_max"]
                cube_list = iris.cube.CubeList([current_cube, new_cube])
                yearly_averages = cube_list.concatenate_cube()
                iris.save(yearly_averages, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            vmin, vmax = self.compute_presentation_value_range(new_cube)
            new_cube.attributes["presentation_min"] = vmin
            new_cube.attributes["presentation_max"] = vmax
            iris.save(new_cube, dst)
            return
    
    def compute_presentation_value_range(self, cube):
        mean = np.ma.mean(cube.data)
        delta = np.ma.max(cube.data) - mean
        vmin = mean - 1.2 * delta
        vmax = mean + 1.2 * delta
        return vmin, vmax