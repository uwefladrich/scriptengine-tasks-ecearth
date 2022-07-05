"""Processing Task that creates a 2D map of a given extensive atmosphere quantity."""
from pathlib import Path

import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .map import Map


class OifsAllMeanMap(Map):
    """OifsAllMeanMap Processing Task"""

    _required_arguments = (
        "src",
        "dst",
        "varname",
    )

    def __init__(self, arguments=None):
        OifsAllMeanMap.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = Path(self.getarg("dst", context))
        varname = self.getarg("varname", context)
        self.log_info(f"Create map for atmosphere variable {varname} at '{dst}'.")
        self.log_debug(f"Source file: {src}")

        self.check_file_extension(dst)

        oifs_cube = helpers.cubes.load_input_cube(src, varname)

        map_cube = self.compute_time_mean(oifs_cube)

        self.set_cell_methods(map_cube)
        map_cube = self.adjust_metadata(map_cube, varname)
        self.save(map_cube, dst)

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
        # Promote time from scalar to climatological coordinate
        time_mean_cube.coord("time").climatological = True
        return time_mean_cube

    def set_cell_methods(self, map_cube):
        """Add the correct cell methods."""
        map_cube.cell_methods = ()
        map_cube.add_cell_method(
            iris.coords.CellMethod(
                "mean within years", coords="time", intervals="1 year"
            )
        )
        map_cube.add_cell_method(
            iris.coords.CellMethod("mean over years", coords="time")
        )
        map_cube.add_cell_method(
            iris.coords.CellMethod("point", coords=["latitude", "longitude"])
        )

    def adjust_metadata(self, map_cube, varname: str):
        """Do further adjustments to the cube metadata before saving."""
        # Prevent float32/float64 concatenation errors
        map_cube.data = map_cube.data.astype("float64")
        # Add File Metadata
        map_cube = helpers.cubes.set_metadata(
            map_cube,
            title=f"{map_cube.long_name} (annual mean climatology)",
            comment=f"Simulation average of **{varname}**.",
            map_type="global atmosphere",
        )
        # Convert unit to °C if varname is given in K
        if map_cube.units.name == "kelvin":
            map_cube.convert_units("degC")
        return map_cube
