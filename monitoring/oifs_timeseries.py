"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import warnings
from pathlib import Path

import iris
from iris.analysis import WeightedAggregator
from iris.coords import CellMeasure
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .timeseries import Timeseries


class OifsTimeseries(Timeseries):
    """OifsTimeseries Processing Task"""

    _required_arguments = (
        "src",
        "varname",
        "dst",
    )

    def __init__(self, arguments):
        OifsTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    def _load_input(self, context):
        src = self.getarg("src", context)
        var_name = self.getarg("varname", context)
        self.log_info(f"Create time series for atmosphere variable {var_name}.")
        self.log_debug(f"Source file(s): {src}")

        var_data = helpers.cubes.load_input_cube(src, var_name)
        return var_data

    def _adjust_metadata(self, cube):
        """Adjustments to the cube metadata before saving."""
        long_name = cube.long_name
        var_name = cube.standard_name
        comment = f"Annual mean of {long_name} / **{var_name}**."
        cube.add_cell_method(
            iris.coords.CellMethod("mean", coords="time", intervals="1 year")
        )
        cube = helpers.cubes.set_metadata(
            cube,
            title=f"{long_name} (annual mean)",
            comment=comment,
        )
        return helpers.cubes.convert_units(cube)

    def _compute_global_aggregate(self, cube, operation: WeightedAggregator):
        """Area-weighted aggregate of cube (e.g., sum, mean)."""
        area_weights = helpers.cubes.compute_area_weights(cube)
        cell_size = CellMeasure(
            area_weights, var_name="cell_size", units="m2", measure="area"
        )
        dims = tuple(range(len(area_weights.shape)))
        cube.add_cell_measure(cell_size, dims)
        # Remove duplicate boundary values before averaging
        cube.coord("latitude").bounds = cube.coord("latitude").bounds[:, [0, 1]]
        cube.coord("longitude").bounds = cube.coord("longitude").bounds[:, [0, 1]]
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                "ignore",
                "Collapsing a non-contiguous coordinate.",
                UserWarning,
            )
            global_aggregate = cube.collapsed(
                ["latitude", "longitude"],
                operation,
                weights="cell_size",
            )
        return global_aggregate


class OifsGlobalMeanYearMeanTimeseries(OifsTimeseries):
    """OifsGlobalMeanYearMeanTimeseries Processing Task"""

    _required_arguments = ("src", "dst", "varname")

    def __init__(self, arguments=None):
        OifsGlobalMeanYearMeanTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    @timed_runner
    def run(self, context):
        oifs_cube = self._load_input(context)

        global_mean = self._compute_global_aggregate(oifs_cube, iris.analysis.MEAN)
        annual_mean = helpers.cubes.compute_annual_mean(global_mean)
        annual_mean.cell_methods = (iris.coords.CellMethod("mean", coords="area"),)

        annual_mean = self._adjust_metadata(annual_mean)

        dst = Path(self.getarg("dst", context))
        self.check_file_extension(dst)
        self.save(annual_mean, dst)


class OifsGlobalSumYearMeanTimeseries(OifsTimeseries):
    """OifsGlobalSumYearMeanTimeseries Processing Task"""

    _required_arguments = ("src", "dst", "varname")

    def __init__(self, arguments=None):
        OifsGlobalSumYearMeanTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    @timed_runner
    def run(self, context):
        oifs_cube = self._load_input(context)

        global_sum = self._compute_global_aggregate(oifs_cube, iris.analysis.SUM)
        annual_mean = helpers.cubes.compute_annual_mean(global_sum)
        annual_mean.cell_methods = (iris.coords.CellMethod("sum", coords="area"),)

        annual_mean = self._adjust_metadata(annual_mean)

        dst = Path(self.getarg("dst", context))
        self.check_file_extension(dst)
        self.save(annual_mean, dst)
