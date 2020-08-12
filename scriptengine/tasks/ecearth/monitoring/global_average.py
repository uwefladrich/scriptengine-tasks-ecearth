"""Processing Task that calculates the annual global average of a given extensive quantity."""

import warnings

import iris

from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as hlp
from .time_series import TimeSeries

class GlobalAverage(TimeSeries):
    """GlobalAverage Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "domain",
            "varname",
        ]
        super(TimeSeries, self).__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        domain = self.getarg('domain', context)
        varname = self.getarg('varname', context)
        comment = (f"Global average time series of **{varname}**. "
                   f"Each data point represents the (spatial and temporal) "
                   f"average over one leg.")
        self.log_info(f"Create time series for ocean variable {varname} at {dst}.")
        self.log_debug(f"Domain: {domain}, Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_error((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        leg_cube = hlp.load_input_cube(src, varname)

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
                weights=hlp.compute_spatial_weights(domain, leg_cube.shape),
                )
        # Remove auxiliary time coordinate before collapsing cube
        spatial_avg.remove_coord(spatial_avg.coord('time', dim_coords=False))
        ann_spatial_avg = spatial_avg.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=hlp.compute_time_weights(spatial_avg),
        )
        # Promote time from scalar to dimension coordinate
        ann_spatial_avg = iris.util.new_axis(ann_spatial_avg, 'time')

        ann_spatial_avg = hlp.set_metadata(
            ann_spatial_avg,
            title=f'{ann_spatial_avg.long_name} (Annual Mean)',
            comment=comment,
            diagnostic_type=self.diagnostic_type,
            )

        ann_spatial_avg.cell_methods = ()
        ann_spatial_avg.add_cell_method(iris.coords.CellMethod('mean', coords='time', intervals='1 month'))
        ann_spatial_avg.add_cell_method(iris.coords.CellMethod('mean', coords='area'))

        self.save(ann_spatial_avg, dst)
