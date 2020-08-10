"""Processing Task that calculates the SYPD over time."""

import os

import iris
import numpy as np

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers

class SYPD(Task):
    """SYPD Processing Task"""
    def __init__(self, parameters):
        required = [
            "dst",
            "start",
            "end",
            "leg",
            "time",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"SYPD development during the current model run.")
        self.type = "time series"

    @timed_runner
    def run(self, context):
        dst = self.getarg('dst', context)
        start = self.getarg('start', context)
        end = self.getarg('end', context)
        time = self.getarg('time', context)
        leg = self.getarg('leg', context)
        self.log_info(f"Create SYPD time series at {dst}.")
        self.log_debug(f"Start: {start}, End: {end}, elapsed time: {time}, leg: {leg}.")

        if not dst.endswith(".nc"):
            self.log_error((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        leg_span = end - start
        sypd = leg_span.total_seconds()/time/365

        coord = iris.coords.DimCoord(
            points=np.array([leg]),
            long_name="leg number",
            var_name="leg",
            bounds=np.array([[leg - 1, leg]]),
        )

        sypd_cube = iris.cube.Cube(
            data=np.array([sypd]),
            long_name="Simulated Years per Day",
            var_name="sypd",
            units="1",
            dim_coords_and_dims=[(coord,0)],      
        )

        sypd_cube = helpers.set_metadata(
            sypd_cube,
            title='Simulated Years per Day',
            comment=self.comment,
            diagnostic_type=self.type,
            )

        self.save_cube(sypd_cube, dst)

    def save_cube(self, new_cube, dst):
        """save global average cubes in netCDF file"""
        try:
            current_cube = iris.load_cube(dst)
            current_bounds = current_cube.coord('leg number').bounds
            new_bounds = new_cube.coord('leg number').bounds
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