"""Processing Task that writes out a generalized time series diagnostic."""

import os
import datetime

import iris
import numpy as np

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers

class TimeSeries(Task):
    """Processing Task that writes out a generalized time series diagnostic."""

    diagnostic_type = 'time series'

    def __init__(self, parameters):
        required = [
            "title",
            "coord_value",
            "data_value",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        # load input parameters
        title = self.getarg('title', context)
        data_value = self.getarg('data_value', context)
        dst = self.getarg('dst', context)
        coord_value = self.getarg('coord_value', context)
        data_units = self.getarg('data_units', context, default='1')
        coord_name = self.getarg('coord_name', context, default='time')
        coord_bounds = self.getarg('coord_bounds', context, default=None)
        comment = self.getarg('comment', context, default=".")

        # deal with date/datetime
        coord_value, coord_units = self.value_to_numeric(context, coord_value)
        if coord_bounds is not None:
            coord_bounds = [self.value_to_numeric(context, bound)[0] for bound in coord_bounds]

        self.log_info(f"Create time series at {dst}.")
        self.log_debug(f"Value: {data_value} at time: {coord_value}, title: {title}")

        if not dst.endswith(".nc"):
            self.log_error((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        # create coord
        coord = iris.coords.DimCoord(
            points=np.array([coord_value]),
            long_name=coord_name,
            var_name=coord_name.replace(" ", "_"),
            bounds=np.array([coord_bounds]),
            units=coord_units,
        )

        # create cube
        data_cube = iris.cube.Cube(
            data=np.array([data_value]),
            long_name=title,
            var_name=title.replace(" ", "_"),
            units=data_units,
            dim_coords_and_dims=[(coord, 0)],
        )

        # set metadata
        data_cube = helpers.set_metadata(
            data_cube,
            title=title,
            comment=comment,
            type=self.diagnostic_type,
        )
        self.save(data_cube, dst)


    def save(self, new_cube, dst):
        """save time series cube in netCDF file"""
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
            self.log_warning("Cube will not be saved.")

        # remove temporary save
        os.remove('temp.nc')

    def value_to_numeric(self, context, coord_value):
        """
        convert coordinate value from date(time) object to numeric value if necessary
        """

        if isinstance(coord_value, datetime.datetime):
            since = datetime.datetime(1900, 1, 1)
            coord_units = "second since 1900-01-01 00:00:00"
            seconds = (coord_value - since).total_seconds()
            return seconds, coord_units

        if isinstance(coord_value, datetime.date):
            since = datetime.datetime(1900, 1, 1)
            date_time = datetime.datetime(
                coord_value.year,
                coord_value.month,
                coord_value.day,
                )
            coord_units = "second since 1900-01-01 00:00:00"
            seconds = (date_time - since).total_seconds()
            return seconds, coord_units

        coord_units = self.getarg('coord_units', context, default='1')
        return coord_value, coord_units

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
