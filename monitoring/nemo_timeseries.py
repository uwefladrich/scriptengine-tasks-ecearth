"""Processing Tasks for computing Timeseries from NEMO output."""

from pathlib import Path

import iris
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError
from scriptengine.tasks.core import timed_runner

import helpers.cubes
import helpers.nemo

from .timeseries import Timeseries


class NemoTimeseries(Timeseries):
    """NemoTimeseries Processing Task"""

    _required_arguments = (
        "src",
        "varname",
        "dst",
    )

    def __init__(self, arguments):
        NemoTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    def _load_input(self, context):
        src = self.getarg("src", context)
        var_name = self.getarg("varname", context)
        self.log_info(f"Create time series for ocean variable {var_name}.")

        var_data = helpers.cubes.load_input_cube(src, var_name)
        return var_data


class NemoGlobalSumYearMeanTimeseries(NemoTimeseries):
    _required_arguments = ("domain",)

    def __init__(self, arguments):
        NemoGlobalSumYearMeanTimeseries.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        var_data = self._load_input(context)

        domain = self.getarg("domain", context)
        grid = self.getarg("grid", context, default="T")
        global_sum = helpers.nemo.compute_global_aggregate(
            var_data, domain, grid, iris.analysis.SUM
        )

        annual_mean = helpers.cubes.compute_annual_mean(global_sum)

        annual_mean.cell_methods = (
            iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
            iris.coords.CellMethod(
                "sum",
                coords=(
                    ("area", helpers.nemo.depth_coord(annual_mean).name())
                    if helpers.nemo.has_depth(annual_mean)
                    else "area"
                ),
            ),
        )

        long_name = annual_mean.long_name
        var_name = annual_mean.standard_name
        comment = f"Product of {long_name} / **{var_name}** and grid-cell area, summed over all grid cells."
        annual_mean = helpers.cubes.set_metadata(
            annual_mean,
            title=f"{long_name} (annual mean)",
            comment=comment,
        )

        dst = Path(self.getarg("dst", context))
        self.check_file_extension(dst)
        self.save(annual_mean, dst)


class NemoGlobalMeanYearMeanTimeseries(NemoTimeseries):
    _required_arguments = ("domain",)

    def __init__(self, arguments):
        NemoGlobalMeanYearMeanTimeseries.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        var_data = self._load_input(context)

        domain = self.getarg("domain", context)
        grid = self.getarg("grid", context, default="T")
        global_mean = helpers.nemo.compute_global_aggregate(
            var_data, domain, grid, iris.analysis.MEAN
        )

        annual_mean = helpers.cubes.compute_annual_mean(global_mean)

        annual_mean.cell_methods = (
            iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
            iris.coords.CellMethod(
                "mean",
                coords=(
                    ("area", helpers.nemo.depth_coord(annual_mean).name())
                    if helpers.nemo.has_depth(annual_mean)
                    else "area"
                ),
            ),
        )

        long_name = annual_mean.long_name
        var_name = annual_mean.standard_name
        comment = f"Global mean of {long_name} / **{var_name}**."

        annual_mean = helpers.cubes.set_metadata(
            annual_mean,
            title=f"{long_name} (annual mean)",
            comment=comment,
        )

        dst = Path(self.getarg("dst", context))
        self.check_file_extension(dst)
        self.save(annual_mean, dst)


class NemoYearMeanTimeseries(NemoTimeseries):
    @timed_runner
    def run(self, context):
        var_data = self._load_input(context)

        if not var_data.ndim == 1:
            self.log_error(f"Input data is not one-dimensional.")
            raise ScriptEngineTaskArgumentInvalidError

        annual_mean = helpers.cubes.compute_annual_mean(var_data)

        annual_mean.cell_methods = (
            iris.coords.CellMethod("mean", coords="time", intervals="1 year"),
        )

        long_name = annual_mean.long_name
        var_name = annual_mean.standard_name
        comment = f"Annual mean of {long_name} / **{var_name}**."

        annual_mean = helpers.cubes.set_metadata(
            annual_mean,
            title=f"{long_name} (annual mean)",
            comment=comment,
        )

        dst = Path(self.getarg("dst", context))
        self.check_file_extension(dst)
        self.save(annual_mean, dst)
