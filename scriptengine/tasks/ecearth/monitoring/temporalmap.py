"""Base class for temporal map processing tasks."""

import os

import iris
import numpy as np

from scriptengine.tasks.base import Task

class Temporalmap(Task):
    """Temporalmap Processing Task"""

    def __init__(self, parameters, required_parameters = None):
        super().__init__(__name__, parameters, required_parameters)

    def run(self, context):
        raise NotImplementedError('Base class function Temporalmap.run() must not be called')

    def save(self, new_cube, dst):
        """save temporal map cube in netCDF file"""
        self.log_debug(f"Saving temporal map cube to {dst}")
        new_cube.attributes['diagnostic_type'] = 'temporal map'
        try:
            current_cube = iris.load_cube(dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return

        # Iris changes metadata when saving/loading cube
        # save & reload to prevent metadata mismatch
        iris.save(new_cube, 'temp.nc')
        new_cube = iris.load_cube('temp.nc')

        current_bounds = current_cube.coord('time').bounds
        new_bounds = new_cube.coord('time').bounds
        if not current_bounds[-1][-1] > new_bounds[0][0]:
            new_cube.attributes = current_cube.attributes
            cube_list = iris.cube.CubeList([current_cube, new_cube])
            merged_cube = cube_list.concatenate_cube()
            iris.save(merged_cube, f"{dst}-copy.nc")
            os.remove(dst)
            os.rename(f"{dst}-copy.nc", dst)
        else:
            self.log_warning("Non-monotonic coordinate. Cube will not be saved.")
        # remove temporary save
        os.remove('temp.nc')

    def correct_file_extension(self, dst):
        """check if destination file has a valid netCDF extension"""
        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return False
        return True
