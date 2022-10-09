"""Processing Task that creates a 2D map of a given extensive ocean quantity."""
from pathlib import Path

import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .map import Map


class NemoAllMeanMap(Map):
    """NemoAllMeanMap Processing Task"""

    _required_arguments = (
        "src",
        "dst",
        "varname",
    )

    def __init__(self, arguments=None):
        NemoAllMeanMap.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = Path(self.getarg("dst", context))
        varname = self.getarg("varname", context)
        self.log_info(f"Create map for ocean variable {varname} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        self.check_file_extension(dst)

        leg_cube = helpers.cubes.load_input_cube(src, varname)

        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord("time", dim_coords=False))

        time_weights = helpers.cubes.compute_time_weights(leg_cube, leg_cube.shape)
        leg_average = leg_cube.collapsed(
            "time", iris.analysis.MEAN, weights=time_weights
        )

        leg_average.coord("time").climatological = True
        leg_average = self.set_cell_methods(leg_average)

        leg_average = helpers.cubes.set_metadata(
            leg_average,
            title=f"{leg_average.long_name} (annual mean climatology)",
            comment=f"Simulation average of **{varname}**.",
            map_type="global ocean",
        )

        self.save(leg_average, dst)

    def set_cell_methods(self, cube):
        """Set the correct cell methods."""
        cube.cell_methods = ()
        cube.add_cell_method(
            iris.coords.CellMethod(
                "mean within years", coords="time", intervals="1 month"
            )
        )
        cube.add_cell_method(iris.coords.CellMethod("mean over years", coords="time"))
        cube.add_cell_method(
            iris.coords.CellMethod("point", coords=["latitude", "longitude"])
        )
        return cube
