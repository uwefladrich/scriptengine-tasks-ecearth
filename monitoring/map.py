"""Base class for map processing tasks."""

import os

import iris
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError, ScriptEngineTaskRunError

from scriptengine.tasks.core import Task
import helpers.file_handling as helpers

class Map(Task):
    """Map Processing Task"""

    def run(self, context):
        raise NotImplementedError('Base class function Map.run() must not be called')

    def save(self, new_cube, dst):
        """save map cube in netCDF file"""
        self.log_debug(f"Saving map cube to {dst}")
        new_cube.attributes['diagnostic_type'] = 'map'
        try:
            current_cube = iris.load_cube(dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return

        current_bounds = current_cube.coord('time').bounds
        new_bounds = new_cube.coord('time').bounds
        if current_bounds[-1][-1] > new_bounds[0][0]:
            msg = "Non-monotonic coordinate. Cube will not be saved."
            self.log_error(msg)
            raise ScriptEngineTaskRunError(msg)

        # Iris changes metadata when saving/loading cube
        # save & reload to prevent metadata mismatch
        iris.save(new_cube, 'temp.nc')
        new_cube = iris.load_cube('temp.nc')

        current_cube.cell_methods = new_cube.cell_methods
        cube_list = iris.cube.CubeList([current_cube, new_cube])
        merged_cube = cube_list.merge_cube()
        simulation_avg = self.compute_simulation_avg(merged_cube)
        iris.save(simulation_avg, f"{dst}-copy.nc")
        os.remove(dst)
        os.rename(f"{dst}-copy.nc", dst)   
        # remove temporary save
        os.remove('temp.nc')

    def check_file_extension(self, dst):
        """check if destination file has a valid netCDF extension"""
        if not dst.endswith(".nc"):
            msg = (
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            )
            self.log_error(msg)
            raise ScriptEngineTaskArgumentInvalidError(msg)

    def compute_simulation_avg(self, merged_cube):
        """
        Compute Time Average for the whole simulation.
        """
        self.log_debug("Computing simulation average.")
        time_weights = helpers.compute_time_weights(merged_cube, merged_cube.shape)
        simulation_avg = merged_cube.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=time_weights,
        )
        return simulation_avg
