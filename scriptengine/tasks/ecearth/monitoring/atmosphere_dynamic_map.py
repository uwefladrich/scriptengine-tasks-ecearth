"""Processing Task that creates a 2D dynamic map of a given extensive atmosphere quantity."""

import os

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base import Task
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
        self.comment = (f"Dynamic Map of **{self.grib_code}**.")
        self.type = "dynamic map"
        self.map_type = "global atmosphere"

    def run(self, context):
        create_leg_mean = True
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        self.log_info(f"Create dynamic map for atmosphere variable {grib_code} at {dst}.")
        self.log_debug(f"Source file(s): {src}")

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        cf_phenomenon = iris_grib.grib_phenom_translation.grib1_phenom_to_cf_info(
            128, # table
            98, # institution: ECMWF
            grib_code
        )
        if cf_phenomenon: # is None if not found
            constraint = cf_phenomenon.standard_name
        else:
            constraint = f"UNKNOWN LOCAL PARAM {grib_code}.128"

        leg_cube = helpers.load_input_cube(src, constraint)

        if create_leg_mean:
            annual_avg = leg_cube.collapsed(
                'time',
                iris.analysis.MEAN,
            )

            # Promote time from scalar to dimension coordinate
            annual_avg = iris.util.new_axis(annual_avg, 'time')

            annual_avg.var_name = f"param_{grib_code}"
            if not annual_avg.long_name:
                annual_avg.long_name = annual_avg.var_name

            annual_avg = helpers.set_metadata(
                annual_avg,
                title=f'{annual_avg.long_name.title()} {self.type.title()}',
                comment=f'Annual Average {self.comment}',
                diagnostic_type=self.type,
                map_type=self.map_type,
            )
            if annual_avg.units.name == 'kelvin':
                annual_avg.convert_units('degC')

            iris.save(annual_avg, 'temp.nc')
            annual_avg = iris.load_cube('temp.nc')
            self.save_cube(annual_avg, dst)
            os.remove('temp.nc')
        else:
            leg_cube = helpers.set_metadata(
                leg_cube,
                title=f'{leg_cube.long_name.title()} {self.type.title()}',
                comment=f'Monthly Average {self.comment}',
                diagnostic_type=self.type,
                map_type=self.map_type,
            )
            iris.save(leg_cube, 'temp.nc')
            leg_cube = iris.load_cube('temp.nc')
            self.save_cube(leg_cube, dst)
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
