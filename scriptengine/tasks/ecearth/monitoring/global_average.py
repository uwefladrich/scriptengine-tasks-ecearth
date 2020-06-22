"""Processing Task that calculates the global yearly average of a given extensive quantity."""

import os
import warnings

import iris

from scriptengine.tasks.base import Task
import helpers.file_handling as helpers

class GlobalAverage(Task):
    """GlobalAverage Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "domain",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global average time series of **{self.varname}**. "
                        f"Each data point represents the (spatial and temporal) "
                        f"average over one leg.")
        self.type = "time series"

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        domain = self.getarg('domain', context)
        varname = self.getarg('varname', context)
        self.log_info(f"Create time series for ocean variable {varname} at {dst}.")
        self.log_debug(f"Domain: {domain}, Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        leg_cube = helpers.load_input_cube(src, varname)

        cell_weights = helpers.compute_spatial_weights(domain, leg_cube.shape)
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                'ignore',
                "Collapsing a multi-dimensional coordinate.",
                UserWarning,
                )
            spatial_avg = leg_cube.collapsed(
                ['latitude', 'longitude'],
                iris.analysis.MEAN,
                weights=cell_weights,
                )
        month_weights = helpers.compute_time_weights(spatial_avg)
        # Remove auxiliary time coordinate before collapsing cube
        spatial_avg.remove_coord(spatial_avg.coord('time', dim_coords=False))
        ann_spatial_avg = spatial_avg.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=month_weights)
        # Promote time from scalar to dimension coordinate
        ann_spatial_avg = iris.util.new_axis(ann_spatial_avg, 'time')

        ann_spatial_avg = helpers.set_metadata(
            ann_spatial_avg,
            title=f'{ann_spatial_avg.long_name} (Global Average Time Series)',
            comment=self.comment,
            diagnostic_type=self.type,
            )

        self.save_cube(ann_spatial_avg, dst)

    def save_cube(self, new_cube, dst):
        """save global average cubes in netCDF file"""
        try:
            current_cube = iris.load_cube(dst)
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
        