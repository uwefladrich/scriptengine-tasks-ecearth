"""Processing Task that creates a temporal map of a given 2D extensive ocean quantity."""

import iris

from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers
from .temporalmap import Temporalmap

class NemoTimeMeanTemporalmap(Temporalmap):
    """NemoTimeMeanTemporalmap Processing Task"""

    def __init__(self, parameters, required_parameters = None):
        super().__init__(
            parameters,
            required_parameters=['src', 'dst', 'varname'] + (required_parameters or [])
            )

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        varname = self.getarg('varname', context)
        self.log_info(f"Create temporal map for ocean variable {varname} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not self.correct_file_extension(dst):
            return

        leg_cube = helpers.load_input_cube(src, varname)

        # Remove auxiliary time coordinate before collapsing cube
        leg_cube.remove_coord(leg_cube.coord('time', dim_coords=False))

        processed_cube = self.time_operation(varname, leg_cube)
        self.save(processed_cube, dst)
    
    def time_operation(self, varname, leg_cube):
        raise NotImplementedError('Base class function NemoTimeMeanTemporalmap.time_operation() must not be called')

class NemoYearMeanTemporalmap(NemoTimeMeanTemporalmap):
    """NemoYearMeanTemporalmap Processing Task"""

    def __init__(self, parameters):
        super().__init__(parameters)

    def time_operation(self, varname, leg_cube):
        self.log_debug("Creating an annual mean.")
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
            map_type="global ocean",
        )
        leg_average.cell_methods = ()
        leg_average.add_cell_method(iris.coords.CellMethod('mean', coords='time', intervals='1 month'))
        leg_average.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))
        return leg_average

class NemoMonthMeanTemporalmap(NemoTimeMeanTemporalmap):
    """NemoMonthMeanTemporalmap Processing Task"""

    def __init__(self, parameters):
        super().__init__(parameters)

    def time_operation(self, varname, leg_cube):
        self.log_debug("Creating monthly means.")
        leg_cube = helpers.set_metadata(
            leg_cube,
            title=f'{leg_cube.long_name.title()} (Monthly Mean Map)',
            comment=f"Monthly Mean of **{varname}**.",
            map_type='global ocean',
        )
        leg_cube.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))
        return leg_cube
