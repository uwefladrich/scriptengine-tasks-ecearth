"""Processing Task that creates a 2D dynamic map of a given extensive atmosphere quantity."""

import os

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from helpers.grib_cf_additions import update_grib_mappings
import helpers.file_handling as helpers

class AtmosphereDynamicMap(Task):
    """AtmosphereDynamicMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "grib_code",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Leg Mean Dynamic Map of **{self.grib_code}**.")
        self.type = "dynamic map"
        self.map_type = "global atmosphere"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        src = [path for path in src if not path.endswith('000000')]
        self.log_info(f"Create dynamic map for atmosphere variable {grib_code} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_error((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        update_grib_mappings()
        cf_phenomenon = iris_grib.grib_phenom_translation.grib1_phenom_to_cf_info(
            128, # table
            98, # institution: ECMWF
            grib_code
        )
        if not cf_phenomenon:
            self.log_error(f"CF Phenomenon for {grib_code} not found. Update local table?")
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
        leg_mean.cell_methods = ()
        leg_mean.add_cell_method(iris.coords.CellMethod('mean', coords='time', intervals=f'{step} seconds'))
        leg_mean.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))
        # Promote time from scalar to dimension coordinate
        leg_mean = iris.util.new_axis(leg_mean, 'time')

        leg_mean = helpers.set_metadata(
            leg_mean,
            title=f'{leg_mean.long_name.title()} (Annual Mean Map)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )

        iris.save(leg_mean, 'temp.nc')
        leg_mean = iris.load_cube('temp.nc')
        self.save_cube(leg_mean, dst)
        os.remove('temp.nc')

    def save_cube(self, new_cube, dst):
        """save cube in netCDF file"""
        try:
            current_cube = iris.load_cube(dst)
            current_bounds = current_cube.coord('time').bounds
            new_bounds = new_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                new_cube.attributes["presentation_min"] = current_cube.attributes["presentation_min"]
                new_cube.attributes["presentation_max"] = current_cube.attributes["presentation_max"]
                cube_list = iris.cube.CubeList([current_cube, new_cube])
                yearly_averages = cube_list.concatenate_cube()
                iris.save(yearly_averages, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            vmin, vmax = self.compute_presentation_value_range(new_cube)
            new_cube.attributes["presentation_min"] = vmin
            new_cube.attributes["presentation_max"] = vmax
            iris.save(new_cube, dst)
            return

    def compute_presentation_value_range(self, cube):
        mean = np.ma.mean(cube.data)
        delta = np.ma.max(cube.data) - mean
        vmin = mean - 1.2 * delta
        vmax = mean + 1.2 * delta
        return vmin, vmax
