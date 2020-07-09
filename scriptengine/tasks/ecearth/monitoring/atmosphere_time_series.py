"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import os
import warnings

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from helpers.grib_cf_additions import update_grib_mappings
import helpers.file_handling as helpers

class AtmosphereTimeSeries(Task):
    """AtmosphereMap Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "grib_code",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global average time series of **{self.grib_code}**. "
                        f"Each data point represents the (spatial and temporal) "
                        f"average over one leg.")
        self.type = "time series"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        src = [path for path in src if not path.endswith('000000')]
        self.log_info(f"Create time series for atmosphere variable {grib_code} at {dst}.")
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

        self.log_debug("Averaging over the leg.")
        leg_mean = leg_cube.collapsed(
            'time',
            iris.analysis.MEAN,
        )

        area_weights = self.get_area_weights(leg_mean)
        self.log_debug("Averaging over space.")
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                'ignore',
                "Collapsing a non-contiguous coordinate.",
                UserWarning,
                )
            spatial_mean = leg_mean.collapsed(
                ['latitude', 'longitude'],
                iris.analysis.MEAN,
                weights=area_weights,
            )
        
        spatial_mean.cell_methods = ()
        spatial_mean.add_cell_method(iris.coords.CellMethod('mean', coords='time', intervals=f'{step} seconds'))
        spatial_mean.add_cell_method(iris.coords.CellMethod('mean', coords='area'))

        # Promote time from scalar to dimension coordinate
        spatial_mean = iris.util.new_axis(spatial_mean, 'time')

        spatial_mean.long_name = spatial_mean.long_name.replace("_", " ")

        spatial_mean = helpers.set_metadata(
            spatial_mean,
            title=f'{spatial_mean.long_name} (Annual Mean)',
            comment=self.comment,
            diagnostic_type=self.type,
        )

        if spatial_mean.units.name == 'kelvin':
            spatial_mean.convert_units('degC')
        iris.save(spatial_mean, 'temp.nc') # Iris changes metadata when saving/loading cube
        spatial_mean = iris.load_cube('temp.nc')
        self.save_cube(spatial_mean, dst)
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
                cube_list = iris.cube.CubeList([current_cube, new_cube])
                merged_cube = cube_list.concatenate_cube()
                iris.save(merged_cube, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            iris.save(new_cube, dst)
            return

    def get_area_weights(self, cube):
        """compute area weights for the reduced gaussian grid"""
        self.log_debug("Getting area weights.")
        nh_latitudes = np.ma.masked_less(cube.coord('latitude').points, 0)
        unique_lats, gridpoints_per_lat = np.unique(nh_latitudes, return_counts=True)
        unique_lats, gridpoints_per_lat = unique_lats[0:-1], gridpoints_per_lat[0:-1]
        areas = []
        last_angle = 0
        earth_radius = 6371
        for latitude, amount in zip(unique_lats, gridpoints_per_lat):
            delta = latitude - last_angle
            current_angle = last_angle + 2 * delta
            sin_diff = np.sin(np.deg2rad(current_angle)) - np.sin(np.deg2rad(last_angle))
            ring_area = 2 * np.pi * earth_radius**2 * sin_diff
            grid_area = ring_area / amount
            areas.extend([grid_area] * amount)
            last_angle = current_angle
        areas = np.append(areas[::-1], areas)
        area_weights = np.broadcast_to(areas, cube.data.shape)
        return area_weights
