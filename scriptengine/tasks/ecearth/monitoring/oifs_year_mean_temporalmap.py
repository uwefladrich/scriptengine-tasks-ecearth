"""Processing Task that creates a 2D time map of a given extensive atmosphere quantity."""

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base.timing import timed_runner

from helpers.grib_cf_additions import update_grib_mappings
import helpers.file_handling as helpers
from .temporalmap import Temporalmap

class OifsYearMeanTemporalmap(Temporalmap):
    """OifsYearMeanTemporalmap Processing Task"""

    def __init__(self, parameters):
        super().__init__(
            parameters,
            required_parameters=['src', 'dst', 'grib_code']
            )

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        src = [path for path in src if not path.endswith('000000')]
        self.log_info(f"Create time map for atmosphere variable {grib_code} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not self.correct_file_extension(dst):
            return

        update_grib_mappings()
        cf_phenomenon = iris_grib.grib_phenom_translation.grib1_phenom_to_cf_info(
            128, # table
            98, # institution: ECMWF
            grib_code
        )
        if not cf_phenomenon:
            self.log_warning(f"CF Phenomenon for {grib_code} not found. Update local table?")
            return
        self.log_debug(f"Getting variable {cf_phenomenon.standard_name}")
        leg_cube = helpers.load_input_cube(src, cf_phenomenon.standard_name)

        leg_cube.long_name = leg_cube.long_name.replace("_", " ")

        if leg_cube.units.name == 'kelvin':
            leg_cube.convert_units('degC')

        time_coord = leg_cube.coord('time')
        step = time_coord.points[1] - time_coord.points[0]
        time_coord.bounds = np.array([[point - step, point] for point in time_coord.points])

        leg_mean = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
        )
        # Promote time from scalar to dimension coordinate
        leg_mean = iris.util.new_axis(leg_mean, 'time')

        leg_mean = self.set_cell_methods(leg_mean, step)

        leg_mean = helpers.set_metadata(
            leg_mean,
            title=f'{leg_mean.long_name.title()} (Annual Mean Map)',
            comment=f"Leg Mean of **{grib_code}**.",
            map_type="global atmosphere",
        )

        self.save(leg_mean, dst)

    def set_cell_methods(self, cube, step):
        """Set the correct cell methods."""
        cube.cell_methods = ()
        cube.add_cell_method(iris.coords.CellMethod(
            'mean',
            coords='time',
            intervals=f'{step * 3600} seconds',
            ))
        cube.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))
        return cube
