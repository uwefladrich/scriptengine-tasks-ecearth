"""Processing Task that creates a 2D time map of a given extensive atmosphere quantity."""

from pathlib import Path

import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .temporalmap import Temporalmap


class OifsYearMeanTemporalmap(Temporalmap):
    """OifsYearMeanTemporalmap Processing Task"""

    _required_arguments = ("src", "dst", "varname")

    def __init__(self, arguments=None):
        OifsYearMeanTemporalmap.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = Path(self.getarg("dst", context))
        varname = self.getarg("varname", context)
        self.log_info(f"Create time map for atmosphere variable {varname} at {dst}.")
        self.log_debug(f"Source file: {src}")

        self.check_file_extension(dst)

        oifs_cube = helpers.cubes.load_input_cube(src, varname)

        temporalmap_cube = self.compute_time_mean(oifs_cube)

        temporalmap_cube = self.set_cell_methods(temporalmap_cube)
        temporalmap_cube = self.adjust_metadata(temporalmap_cube, varname)
        self.save(temporalmap_cube, dst)

    def set_cell_methods(self, cube):
        """Set the correct cell methods."""
        cube.cell_methods = ()
        cube.add_cell_method(
            iris.coords.CellMethod("mean", coords="time", intervals="1 year")
        )
        cube.add_cell_method(
            iris.coords.CellMethod("point", coords=["latitude", "longitude"])
        )
        return cube

    def compute_time_mean(self, output_cube):
        """Apply the temporal average."""
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

    def adjust_metadata(self, temporalmap_cube, varname: str):
        """Do further adjustments to the cube metadata before saving."""
        temporalmap_cube = helpers.cubes.set_metadata(
            temporalmap_cube,
            title=f"{temporalmap_cube.long_name} (annual mean map)",
            comment=f"Annual mean of **{varname}**.",
            map_type="global atmosphere",
        )
        # Convert unit to °C if varname is given in K
        if temporalmap_cube.units.name == "kelvin":
            temporalmap_cube.convert_units("degC")
        return temporalmap_cube
