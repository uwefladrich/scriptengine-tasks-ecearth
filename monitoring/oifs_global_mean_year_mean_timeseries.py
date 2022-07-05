"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import warnings
from pathlib import Path

import iris
import numpy as np
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .timeseries import Timeseries


class OifsGlobalMeanYearMeanTimeseries(Timeseries):
    """OifsGlobalMeanYearMeanTimeseries Processing Task"""

    _required_arguments = ("src", "dst", "varname")

    def __init__(self, arguments=None):
        OifsGlobalMeanYearMeanTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = Path(self.getarg("dst", context))
        varname = self.getarg("varname", context)
        self.log_info(f"Create time series for atmosphere variable {varname} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        self.check_file_extension(dst)

        oifs_cube = helpers.cubes.load_input_cube(src, varname)

        time_mean_cube = self.compute_time_mean(oifs_cube)

        area_weights = self.compute_area_weights(time_mean_cube)
        timeseries_cube = self.compute_spatial_mean(time_mean_cube, area_weights)

        self.set_cell_methods(timeseries_cube)
        timeseries_cube = self.adjust_metadata(timeseries_cube, varname)
        self.save(timeseries_cube, dst)

    def compute_area_weights(self, cube):
        """compute area weights for the reduced gaussian grid"""
        self.log_debug("Computing area weights.")
        nh_latitudes = np.ma.masked_less(cube.coord("latitude").points, 0)
        unique_lats, gridpoints_per_lat = np.unique(nh_latitudes, return_counts=True)
        unique_lats, gridpoints_per_lat = unique_lats[0:-1], gridpoints_per_lat[0:-1]
        areas = []
        last_angle = 0
        earth_radius = 6371
        for latitude, amount in zip(unique_lats, gridpoints_per_lat):
            delta = latitude - last_angle
            current_angle = last_angle + 2 * delta
            sin_diff = np.sin(np.deg2rad(current_angle)) - np.sin(
                np.deg2rad(last_angle)
            )
            ring_area = 2 * np.pi * earth_radius**2 * sin_diff
            grid_area = ring_area / amount
            areas.extend([grid_area] * amount)
            last_angle = current_angle
        areas = np.append(areas[::-1], areas)
        area_weights = np.broadcast_to(areas, cube.data.shape)
        return area_weights

    def set_cell_methods(self, timeseries_cube):
        """add the correct cell methods"""
        timeseries_cube.cell_methods = ()
        timeseries_cube.add_cell_method(
            iris.coords.CellMethod("mean", coords="time", intervals="1 year")
        )
        timeseries_cube.add_cell_method(iris.coords.CellMethod("mean", coords="area"))

    def compute_time_mean(self, output_cube):
        """Apply the temporal average."""
        self.log_debug("Averaging over the time coordinate.")
        # Remove auxiliary time coordinate before collapsing cube
        try:
            output_cube.coord("time")
        except iris.exceptions.CoordinateNotFoundError:
            output_cube.remove_coord(output_cube.coord("time", dim_coords=False))
        time_mean_cube = output_cube.collapsed(
            "time",
            iris.analysis.MEAN,
        )
        # Promote time from scalar to dimension coordinate
        time_mean_cube = iris.util.new_axis(time_mean_cube, "time")
        return time_mean_cube

    def compute_spatial_mean(self, time_mean_cube, area_weights):
        """Apply the spatial average."""
        self.log_debug("Averaging over latitude and longitude.")
        # Remove duplicate boundary values before averaging
        time_mean_cube.coord("latitude").bounds = time_mean_cube.coord(
            "latitude"
        ).bounds[:, [0, 1]]
        time_mean_cube.coord("longitude").bounds = time_mean_cube.coord(
            "longitude"
        ).bounds[:, [0, 2]]
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                "ignore",
                "Collapsing a non-contiguous coordinate.",
                UserWarning,
            )
            spatial_mean_cube = time_mean_cube.collapsed(
                ["latitude", "longitude"],
                iris.analysis.MEAN,
                weights=area_weights,
            )
        return spatial_mean_cube

    def adjust_metadata(self, timeseries_cube, varname: str):
        """Do further adjustments to the cube metadata before saving."""
        # Add File Metadata
        comment = (
            f"Global average time series of **{varname}**. "
            f"Each data point represents the (spatial and temporal) "
            f"average over one year."
        )
        timeseries_cube = helpers.cubes.set_metadata(
            timeseries_cube,
            title=f"{timeseries_cube.long_name} (annual mean)",
            comment=comment,
        )
        # Convert unit to °C if varname is given in K
        if timeseries_cube.units.name == "kelvin":
            timeseries_cube.convert_units("degC")
        return timeseries_cube
