"""Processing Task that creates a 2D dynamic map of a given extensive ocean quantity."""

import iris

from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers
from .dynamic_map import DynamicMap

class OceanDynamicMap(DynamicMap):
    """OceanDynamicMap Processing Task"""

    map_type = "global ocean"

    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "varname",
        ]
        super(DynamicMap, self).__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        create_leg_mean = True
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        varname = self.getarg('varname', context)
        self.log_info(f"Create dynamic map for ocean variable {varname} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not self.correct_file_extension(dst):
            return

        leg_cube = helpers.load_input_cube(src, varname)

        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))

        if create_leg_mean:
            month_weights = helpers.compute_time_weights(leg_cube, leg_cube.shape)
            leg_average = leg_cube.collapsed(
                'time',
                iris.analysis.MEAN,
                weights=month_weights
            )
            # Promote time from scalar to dimension coordinate
            leg_average = iris.util.new_axis(leg_average, 'time')
            leg_average = helpers.set_metadata(
                leg_average,
                title=f'{leg_average.long_name.title()} (Annual Mean Map)',
                comment=f"Leg Mean of **{varname}**.",
                diagnostic_type=self.diagnostic_type,
                map_type=self.map_type,
            )
            leg_average.cell_methods = ()
            leg_average.add_cell_method(iris.coords.CellMethod('mean', coords='time', intervals='1 month'))
            leg_average.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))
            self.save(leg_average, dst)
        else:
            leg_cube = helpers.set_metadata(
                leg_cube,
                title=f'{leg_cube.long_name.title()} (Monthly Mean Map)',
                comment=f"Monthly Mean of **{varname}**.",
                diagnostic_type=self.diagnostic_type,
                map_type=self.map_type,
            )
            leg_average.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))
            self.save(leg_cube, dst)
