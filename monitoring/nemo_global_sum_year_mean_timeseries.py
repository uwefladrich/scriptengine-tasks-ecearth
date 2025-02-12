"""Processing Task that calculates the area-weighted sum and annual mean of a given intensive quantity."""

import warnings
from pathlib import Path

import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes
import helpers.nemo

from .timeseries import Timeseries


class NemoGlobalSumYearMeanTimeseries(Timeseries):
    """NemoGlobalSumYearMeanTimeseries Processing Task"""

    _required_arguments = (
        "src",
        "domain",
        "varname",
        "dst",
    )

    def __init__(self, arguments):
        NemoGlobalSumYearMeanTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = Path(self.getarg("dst", context))
        var_name = self.getarg("varname", context)
        domain = self.getarg("domain", context)
        grid = self.getarg("grid", context, default="T")

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
            global_sum = var_data.collapsed(
                helpers.nemo.spatial_coords(var_data),
                iris.analysis.SUM,
                weights=helpers.nemo.spatial_weights(var_data, domain, grid),
            )
        # Remove auxiliary time coordinate before collapsing cube
        global_sum.remove_coord(global_sum.coord("time", dim_coords=False))
        annual_mean = global_sum.collapsed(
            "time",
            iris.analysis.MEAN,
            weights=helpers.cubes.compute_time_weights(global_sum),
        )
        # Promote time from scalar to dimension coordinate
        annual_mean = iris.util.new_axis(annual_mean, "time")

        long_name = annual_mean.long_name
        comment = f"Product of {long_name} / **{var_name}** and grid-cell area, summed over all grid cells."
        annual_mean = helpers.cubes.set_metadata(
            annual_mean,
            title=f"{long_name} (monthly mean)",
            comment=comment,
        )

        annual_mean.cell_methods = (
            iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
            iris.coords.CellMethod(
                "sum",
                coords=("area", helpers.nemo.depth_coord(annual_mean).name())
                if helpers.nemo.has_depth(annual_mean)
                else "area",
            ),
        )

        self.save(annual_mean, dst)
