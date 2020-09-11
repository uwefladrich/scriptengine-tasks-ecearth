"""Processing Task that writes out a generalized time series diagnostic."""

import os
import datetime

import iris
import numpy as np

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers

class Timeseries(Task):
    """Processing Task that writes out a generalized time series diagnostic."""

    def __init__(self, parameters, required_parameters = None):
        required = [
            "title",
            "coord_value",
            "data_value",
            "dst",
        ]
        super().__init__(
            __name__,
            parameters,
            required_parameters=required + (required_parameters or [])
            )

    @timed_runner
    def run(self, context):
        # load input parameters
        title = self.getarg('title', context)
        dst = self.getarg('dst', context)
        self.log_info(f"Time series {title} at {dst}.")

        # Convert coordinate value to number and get unit
        coord_value = self.getarg("coord_value", context, default=None)
        if type(coord_value) in (datetime.datetime, datetime.date):
            try:
                coord_value = (coord_value - datetime.datetime(1900, 1, 1)).total_seconds()
            except TypeError:
                coord_value = (coord_value - datetime.date(1900, 1, 1)).total_seconds()
            coord_unit = "second since 1900-01-01 00:00:00"
        else:
            coord_unit = self.getarg("coord_unit", context, default="1")
        
        data_value = self.getarg("data_value", context)
        data_unit = self.getarg("data_unit", context, default="1")

        coord_name = self.getarg('coord_name', context, default='time')
        data_name = self.getarg('data_name', context, default=title)
        comment = self.getarg('comment', context, default=".")
        
        self.log_debug(f"Value: {data_value} at time: {coord_value}, title: {title}")

        if not self.correct_file_extension(dst):
            return

        # create coord
        coord = iris.coords.DimCoord(
            points=np.array([coord_value]),
            long_name=coord_name,
            var_name=coord_name.replace(" ", "_"),
            units=coord_unit,
        )

        # create cube
        data_cube = iris.cube.Cube(
            data=np.array([data_value]),
            long_name=data_name,
            var_name=data_name.replace(" ", "_"),
            units=data_unit,
            dim_coords_and_dims=[(coord, 0)],
        )

        # set metadata
        data_cube = helpers.set_metadata(
            data_cube,
            title=title,
            comment=comment,
        )
        self.save(data_cube, dst)

    def save(self, new_cube, dst):
        """save time series cube in netCDF file"""
        self.log_debug(f"Saving time series cube to {dst}")

        new_cube.attributes['diagnostic_type'] = 'time series'
        try:
            current_cube = iris.load_cube(dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return

        # Iris changes metadata when saving/loading cube
        # save & reload to prevent metadata mismatch
        iris.save(new_cube, 'temp.nc')
        new_cube = iris.load_cube('temp.nc')

        if self.test_monotonic_increase(current_cube.coords()[0], new_cube.coords()[0]):
            cube_list = iris.cube.CubeList([current_cube, new_cube])
            merged_cube = cube_list.concatenate_cube()
            iris.save(merged_cube, f"{dst}-copy.nc")
            os.remove(dst)
            os.rename(f"{dst}-copy.nc", dst)
        else:
            self.log_warning("Non-monotonic coordinate. Cube will not be saved.")

        # remove temporary save
        os.remove('temp.nc')

    def test_monotonic_increase(self, old_coord, new_coord):
        """Test if coordinate is monotonically increasing."""
        current_bounds = old_coord.bounds
        new_bounds = new_coord.bounds
        if current_bounds is not None and new_bounds is not None:
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis.")
                return False
            return True

        if old_coord.points[-1] > new_coord.points[0]:
            self.log_warning("Inserting would lead to non-monotonic time axis.")
            return False
        return True

    def correct_file_extension(self, dst):
        """check if destination file has a valid netCDF extension"""
        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return False
        return True
