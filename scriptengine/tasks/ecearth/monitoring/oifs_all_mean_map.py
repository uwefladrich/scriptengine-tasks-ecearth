"""Processing Task that creates a 2D map of a given extensive atmosphere quantity."""

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base.timing import timed_runner
from helpers.grib_cf_additions import update_grib_mappings
import helpers.file_handling as helpers
from .map import Map

class OifsAllMeanMap(Map):
    """OifsAllMeanMap Processing Task"""

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
        self.log_info(f"Create map for atmosphere variable {grib_code} at {dst}.")
        src = [path for path in src if not path.endswith('000000')]
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

        time_coord = leg_cube.coord('time')
        step = time_coord.points[1] - time_coord.points[0]
        time_coord.bounds = np.array([[point - step, point] for point in time_coord.points])

        leg_mean = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
        )
        leg_mean.coord('time').climatological = True
        leg_mean.cell_methods = ()
        leg_mean.add_cell_method(iris.coords.CellMethod('mean within years', coords='time', intervals=f'{step * 3600} seconds'))
        leg_mean.add_cell_method(iris.coords.CellMethod('mean over years', coords='time'))
        leg_mean.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))

        leg_mean.long_name = leg_mean.long_name.replace("_", " ")

        leg_mean = helpers.set_metadata(
            leg_mean,
            title=f'{leg_mean.long_name.title()} (Annual Mean Climatology)',
            comment=f"Simulation Average of **{grib_code}**.",
            map_type='global atmosphere',
        )
        if leg_mean.units.name == 'kelvin':
            leg_mean.convert_units('degC')

        self.save(leg_mean, dst)
