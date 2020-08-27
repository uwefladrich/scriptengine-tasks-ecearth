"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import iris

from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers
from .map import Map

class NemoAllMeanMap(Map):
    """NemoAllMeanMap Processing Task"""

    def __init__(self, parameters):
        super().__init__(
            parameters,
            required_parameters=['src', 'dst', 'varname']
            )

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        varname = self.getarg('varname', context)
        self.log_info(f"Create map for ocean variable {varname} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not self.correct_file_extension(dst):
            return

        leg_cube = helpers.load_input_cube(src, varname)

        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))

        time_weights = helpers.compute_time_weights(leg_cube, leg_cube.shape)
        leg_average = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=time_weights
        )

        leg_average.coord('time').climatological = True
        leg_average = self.set_cell_methods(leg_average)

        leg_average = helpers.set_metadata(
            leg_average,
            title=f'{leg_average.long_name.title()} (Annual Mean Climatology)',
            comment=f"Simulation Average of **{varname}**.",
            map_type='global ocean',
        )

        self.save(leg_average, dst)
    
    def set_cell_methods(self, cube):
        """Set the correct cell methods."""
        cube.cell_methods = ()
        cube.add_cell_method(
            iris.coords.CellMethod('mean within years', coords='time', intervals='1 month')
            )
        cube.add_cell_method(
            iris.coords.CellMethod('mean over years', coords='time')
            )
        cube.add_cell_method(
            iris.coords.CellMethod('point', coords=['latitude', 'longitude'])
            )
        return cube