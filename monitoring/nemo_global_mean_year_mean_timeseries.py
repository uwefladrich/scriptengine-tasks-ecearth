"""Processing Task that calculates the yearly global average of a given extensive quantity."""

import warnings

import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes
import helpers.nemo

from .timeseries import Timeseries


class NemoGlobalMeanYearMeanTimeseries(Timeseries):
    """NemoGlobalMeanYearMeanTimeseries Processing Task"""

    _required_arguments = (
        "src",
        "domain",
        "varname",
        "dst",
    )

    def __init__(self, arguments):
        NemoGlobalMeanYearMeanTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    @timed_runner
    def run(self, context):

        src = self.getarg("src", context)
        dst = self.getarg("dst", context)
        var_name = self.getarg("varname", context)
        domain = self.getarg("domain", context)
        grid = self.getarg("grid", context, default="T")

        comment = (
            f"Global average time series of **{var_name}**. "
            "Each data point represents the (spatial and temporal) "
            "average over one leg."
        )
        self.log_info(f"Create time series for ocean variable {var_name} at {dst}.")
        self.log_debug(f"Domain: {domain}, Source file(s): {src}")

        self.check_file_extension(dst)

        var_data = helpers.cubes.load_input_cube(src, var_name)
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                "ignore",
                "Collapsing a multi-dimensional coordinate.",
                UserWarning,
            )
            global_avg = var_data.collapsed(
                helpers.nemo.spatial_coords(var_data),
                iris.analysis.MEAN,
                weights=helpers.nemo.spatial_weights(var_data, domain, grid),
            )
        # Remove auxiliary time coordinate before collapsing cube
        global_avg.remove_coord(global_avg.coord("time", dim_coords=False))
        global_yearly_avg = global_avg.collapsed(
            "time",
            iris.analysis.MEAN,
            weights=helpers.cubes.compute_time_weights(global_avg),
        )
        # Promote time from scalar to dimension coordinate
        global_yearly_avg = iris.util.new_axis(global_yearly_avg, "time")

        global_yearly_avg = helpers.cubes.set_metadata(
            global_yearly_avg,
            title=f"{global_yearly_avg.long_name} (yearly Mean)",
            comment=comment,
        )

        global_yearly_avg.cell_methods = (
            iris.coords.CellMethod("mean", coords="time", intervals="1 month"),
            iris.coords.CellMethod(
                "mean",
                coords=("area", helpers.nemo.depth_coord(global_yearly_avg).name())
                if helpers.nemo.has_depth(global_yearly_avg)
                else "area",
            ),
        )

        self.save(global_yearly_avg, dst)
