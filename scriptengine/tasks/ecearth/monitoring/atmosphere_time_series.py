"""Processing Task that creates a 2D map of a given extensive ocean quantity."""

import os
import warnings

import iris
import iris_grib
import numpy as np

from scriptengine.tasks.base import Task
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
        self.comment = (f"Yearly Average of **{self.grib_code}**.")
        self.type = "time series"

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        grib_code = self.getarg('grib_code', context)
        self.log_info(f"Create time series for atmosphere variable {grib_code} at {dst}.")
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
        
        self.log_debug("Averaging over year.")
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                'ignore',
                "Collapsing a non-contiguous coordinate.",
                UserWarning,
                )
            annual_avg = leg_cube.collapsed(
                'time',
                iris.analysis.MEAN,
            )

        area_weights = self.get_area_weights(annual_avg)
        self.log_debug("Averaging over space.")
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                'ignore',
                "Collapsing a non-contiguous coordinate.",
                UserWarning,
                )
            spatial_avg = annual_avg.collapsed(
                ['latitude', 'longitude'],
                iris.analysis.MEAN,
                weights=area_weights,
            )

        # Promote time from scalar to dimension coordinate
        spatial_avg = iris.util.new_axis(spatial_avg, 'time')

        spatial_avg.var_name = f'param_{grib_code}'
        if not spatial_avg.long_name:
            spatial_avg.long_name = f'Parameter {grib_code}'

        spatial_avg = helpers.set_metadata(
            spatial_avg,
            title=f'{spatial_avg.long_name} (Global Average Time Series)',
            comment=self.comment,
            diagnostic_type=self.type,
        )
        spatial_avg.remove_coord('originating_centre')
        spatial_avg.remove_coord('forecast_period')
        if spatial_avg.units.name == 'kelvin':
            spatial_avg.convert_units('degC')
        iris.save(spatial_avg, 'temp.nc') # Iris changes metadata when saving/loading cube
        spatial_avg = iris.load_cube('temp.nc')
        self.save_cube(spatial_avg, dst)
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
        self.log_debug("Getting area weights.")
        nh_latitudes = np.ma.masked_less(cube.coord('latitude').points, 0)
        unique_lats, counts = np.unique(nh_latitudes, return_counts=True)
        unique_lats, counts = unique_lats[0:-1], counts[0:-1]
        areas = []
        last_angle = 0
        earth_radius = 6371
        for lat, amount in zip(unique_lats, counts):
            delta = lat - last_angle
            current_angle = last_angle + 2 * delta
            sin_diff = np.sin(np.deg2rad(current_angle)) - np.sin(np.deg2rad(last_angle))
            ring_area = 2 * np.pi * earth_radius**2 * sin_diff
            grid_area = ring_area / amount
            areas.extend([grid_area] * amount)
            last_angle = current_angle
        areas = np.append(areas[::-1], areas)
        area_weights = np.broadcast_to(areas, cube.data.shape)
        return area_weights
