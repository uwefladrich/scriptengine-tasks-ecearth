"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import os

import iris
import iris_grib

from scriptengine.tasks.base import Task
import helpers.file_handling as helpers

class AtmosphereMap(Task):
    """AtmosphereMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "grib_code",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Map of **{self.varname}**.")
        self.type = "map"
        self.map_type = "global atmosphere"

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        varname = self.getarg('varname', context)

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

        annual_avg = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
        )

        # Promote time from scalar to dimension coordinate
        annual_avg = iris.util.new_axis(annual_avg, 'time')

        annual_avg.var_name = varname
        if not annual_avg.long_name:
            annual_avg.long_name = varname

        annual_avg = helpers.set_metadata(
            annual_avg,
            title=f'{annual_avg.long_name} (Yearly Average Map)',
            comment=self.comment,
            diagnostic_type=self.type,
            map_type=self.map_type,
        )
        if annual_avg.units.name == 'kelvin':
            annual_avg.convert_units('degC')
        self.save_cube(annual_avg, varname, dst)

    def save_cube(self, new_cube, varname, dst):
        """save global average cubes in netCDF file"""
        try:
            current_cube = iris.load_cube(dst, varname)
            current_bounds = current_cube.coord('time').bounds
            new_bounds = new_cube.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                cube_list = iris.cube.CubeList([current_cube, new_cube])
                yearly_averages = cube_list.concatenate_cube()
                simulation_avg = self.compute_simulation_avg(yearly_averages)
                iris.save([yearly_averages, simulation_avg], f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return

    def compute_simulation_avg(self, yearly_averages):
        """
        Compute Time Average for the whole simulation.
        """
        simulation_avg = yearly_averages.collapsed(
            'time',
            iris.analysis.MEAN,
        )
        simulation_avg.var_name = simulation_avg.var_name + '_sim_avg'
        simulation_avg.coord('time').var_name = 'time_value'
        # Promote time from scalar to dimension coordinate
        simulation_avg = iris.util.new_axis(simulation_avg, 'time')
        return simulation_avg
