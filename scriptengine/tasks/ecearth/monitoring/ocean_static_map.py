"""Processing Task that creates a 2D static map of a given extensive ocean quantity."""

import os

import iris

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers

class OceanStaticMap(Task):
    """OceanStaticMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Simulation Average Static Map of **{self.varname}**.")
        self.type = "static map"
        self.map_type = "global ocean"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        varname = self.getarg('varname', context)
        self.log_info(f"Create static map for ocean variable {varname} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        leg_cube = helpers.load_input_cube(src, varname)

        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))

        time_weights = helpers.compute_time_weights(leg_cube, leg_cube.shape)
        leg_average = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=time_weights
        )

        # Promote time from scalar to dimension coordinate
        leg_average = iris.util.new_axis(leg_average, 'time')

        leg_average = helpers.set_metadata(
            leg_average,
            title=f'{leg_average.long_name.title()} {self.type.title()}',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )
        try:
            current_static_map = iris.load_cube(dst)
        except OSError: # file does not exist yet.
            iris.save(leg_average, dst)
            return
        else: # file exists
            current_bounds = current_static_map.coord('time').bounds
            new_bounds = leg_average.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                current_static_map.cell_methods = leg_average.cell_methods
                cube_list = iris.cube.CubeList([current_static_map, leg_average])
                single_cube = cube_list.concatenate_cube()
                simulation_avg = self.compute_simulation_avg(single_cube)
                iris.save(simulation_avg, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)

    def compute_simulation_avg(self, concatenated_cube):
        """
        Compute Time Average for the whole simulation.
        """
        time_weights = helpers.compute_time_weights(concatenated_cube, concatenated_cube.shape)
        simulation_avg = concatenated_cube.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=time_weights,
        )
        # Promote time from scalar to dimension coordinate
        simulation_avg = iris.util.new_axis(simulation_avg, 'time')
        return simulation_avg
