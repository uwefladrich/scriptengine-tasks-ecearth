"""Base class for time map processing tasks."""

import os

import iris
import numpy as np

from scriptengine.tasks.base import Task

class TimeMap(Task):
    """TimeMap Processing Task"""

    diagnostic_type = "time map"

    def __init__(self, parameters):
        super().__init__(__name__, parameters)

    def run(self, context):
        pass

    def save(self, new_cube, dst):
        """save time map cube in netCDF file"""
        try:
            current_cube = iris.load_cube(dst)
        except OSError: # file does not exist yet.
            new_cube = self.set_presentation_value_range(new_cube)
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

    def set_presentation_value_range(self, cube):
        """
        set value range for presentation as cube attributes.

        if min and/or max are given (e.g. by user), use those values
        if not, compute bounds using a 20% over/under estimation
        """
        given_min = cube.attributes.get('presentation_min', None)
        given_max = cube.attributes.get('presentation_max', None)

        # both are given
        if given_min is not None and given_max is not None:
            return cube
    
        mean = np.ma.mean(cube.data)

        # one is given
        if given_min is not None:
            delta = np.ma.max(cube.data) - mean
            upper_bound = mean + 1.2 * delta
            cube.attributes['presentation_max'] = upper_bound
            return cube
        if given_max is not None:
            delta = mean - np.ma.min(cube.data)
            lower_bound = mean - 1.2 * delta
            cube.attributes['presentation_min'] = lower_bound
            return cube

        # none is given
        delta = np.ma.max(cube.data) - mean
        lower_bound = mean - 1.2 * delta
        upper_bound = mean + 1.2 * delta
        cube.attributes['presentation_min'] = lower_bound
        cube.attributes['presentation_max'] = upper_bound
        return cube

    def correct_file_extension(self, dst):
        """check if destination file has a valid netCDF extension"""
        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return False
        return True
