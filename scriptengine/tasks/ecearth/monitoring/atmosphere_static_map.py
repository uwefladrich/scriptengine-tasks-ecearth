"""Processing Task that creates a 2D static map of a given extensive atmosphere quantity."""

import os

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from helpers.grib_cf_additions import update_grib_mappings
import helpers.file_handling as helpers

class AtmosphereStaticMap(Task):
    """AtmosphereStaticMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "grib_code",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Simulation Average Map of **{self.grib_code}**.")
        self.type = "static map"
        self.map_type = "global atmosphere"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        self.log_info(f"Create static map for atmosphere variable {grib_code} at {dst}.")
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

        time_coord = leg_cube.coord('time')
        step = time_coord.points[1] - time_coord.points[0]
        time_coord.bounds = np.array([[point - step, point] for point in time_coord.points])

        leg_mean = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
        )
        leg_mean.coord('time').climatological = True
        leg_mean.cell_methods = ()
        leg_mean.add_cell_method(iris.coords.CellMethod('mean within years', coords='time', intervals=f'{step} seconds'))
        leg_mean.add_cell_method(iris.coords.CellMethod('mean over years', coords='time'))
        leg_mean.add_cell_method(iris.coords.CellMethod('point', coords=['latitude', 'longitude']))

        leg_mean.long_name = leg_mean.long_name.replace("_", " ")

        leg_mean = helpers.set_metadata(
            leg_mean,
            title=f'{leg_mean.long_name.title()} (Annual Mean Climatology)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )
        if leg_mean.units.name == 'kelvin':
            leg_mean.convert_units('degC')

        iris.save(leg_mean, 'temp.nc')
        leg_mean = iris.load_cube('temp.nc')
        self.save_cube(leg_mean, dst)
        os.remove('temp.nc')

    def save_cube(self, new_cube, dst):
        """save global average cubes in netCDF file"""
        try:
            current_cube = iris.load_cube(dst)
            current_bounds = current_cube.coord('time').bounds
            new_bounds = new_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                current_cube.cell_methods = new_cube.cell_methods
                cube_list = iris.cube.CubeList([current_cube, new_cube])
                single_cube = cube_list.merge_cube()
                simulation_avg = self.compute_simulation_avg(single_cube)
                iris.save(simulation_avg, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return

    def compute_simulation_avg(self, concatenated_cube):
        """
        Compute Time Average for the whole simulation.
        """
        time_weights = helpers.compute_time_weights(concatenated_cube, concatenated_cube.shape)
        simulation_avg = concatenated_cube.collapsed(
            'time',
            iris.analysis.MEAN,
            weights=time_weights,
        )
        simulation_avg.var_name = simulation_avg.var_name
        return simulation_avg
