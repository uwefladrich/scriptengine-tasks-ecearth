"""Processing Task that calculates the seasonal cycle of sea ice variables in one leg."""

import datetime
import warnings

import iris
import numpy as np
import cf_units
import cftime

from scriptengine.tasks.base.timing import timed_runner
import helpers.file_handling as helpers
from .time_series import TimeSeries

meta_dict = {
    'sivolu':
        {
            'long_name': 'Sea-Ice Volume',
            'standard_name': 'sea_ice_volume',
            'var_name': 'sivol',
            'old_unit': 'm3',
            'new_unit': '1e3 m3',
        },
    'siconc':
        {
            'long_name': 'Sea-Ice Area',
            'standard_name': 'sea_ice_area',
            'var_name': 'siarea',
            'old_unit': 'm2',
            'new_unit': '1e6 m2',
        },
}

class SeaIceTimeSeries(TimeSeries):
    """SeaIceTimeSeries Processing Task"""
    def __init__(self, parameters):
        required = [
            "summer",
            "winter",
            "domain",
            "dst",
            "hemisphere",
            "varname",
        ]
        super(TimeSeries, self).__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        dst = self.getarg('dst', context)
        varname = self.getarg('varname', context)
        hemisphere = self.getarg('hemisphere', context)

        self.log_info(f"Create {varname} time series for {hemisphere}ern hemisphere at {dst}.")

        if varname not in meta_dict:
            self.log_warning((
                f"'varname' must be one of the following: {meta_dict.keys()} "
                f"Diagnostic will not be treated, returning now."
            ))
            return
        long_name = meta_dict[varname]['long_name']

        summer = self.getarg('summer', context)
        winter = self.getarg('winter', context)
        domain = self.getarg('domain', context)
        
        self.log_debug(f"Domain: {domain}, Source file(s): {summer} (summer), {winter} (winter")

        if not hemisphere in ('north', 'south'):
            self.log_warning((
                f"'hemisphere' must be 'north' or 'south' but is '{hemisphere}'."
                f"Diagnostic will not be treated, returning now."
            ))
            return
        if not self.correct_file_extension(dst):
            return

        leg_cube = helpers.load_input_cube([summer, winter], varname)
        cell_weights = helpers.compute_spatial_weights(domain, leg_cube.shape, 'T')
        latitudes = np.broadcast_to(leg_cube.coord('latitude').points, leg_cube.shape)
        if hemisphere == "north":
            leg_cube.data = np.ma.masked_where(latitudes < 0, leg_cube.data)
        else:
            leg_cube.data = np.ma.masked_where(latitudes > 0, leg_cube.data)
        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                'ignore',
                "Collapsing a multi-dimensional coordinate.",
                UserWarning,
                )
            hemispheric_sum = leg_cube.collapsed(
                ['latitude', 'longitude'],
                iris.analysis.SUM,
                weights=cell_weights,
                )

        # Remove auxiliary time coordinate
        hemispheric_sum.remove_coord(hemispheric_sum.coord('time', dim_coords=False))
        hemispheric_sum.standard_name = meta_dict[varname]['standard_name']
        hemispheric_sum.units = cf_units.Unit(meta_dict[varname]['old_unit'])
        hemispheric_sum.convert_units(meta_dict[varname]['new_unit'])
        hemispheric_sum.long_name = f"{long_name} {hemisphere.capitalize()}"
        hemispheric_sum.var_name = meta_dict[varname]['var_name'] + hemisphere[0]

        metadata = {
            'type': self.diagnostic_type,
            'comment': (f"Sum of {long_name}/**{varname}** in March and "
                        f"September on {hemisphere.title()}ern Hemisphere."),
            'title': f"{long_name} (Seasonal Cycle)",
        }
        hemispheric_sum = helpers.set_metadata(hemispheric_sum, **metadata)

        time_coord = hemispheric_sum.coord('time')
        time_coord.bounds = self.get_time_bounds(time_coord)
        hemispheric_sum = self.set_cell_methods(hemispheric_sum, hemisphere)

        self.save(hemispheric_sum, dst)

    def get_time_bounds(self, time_coord):
        """
        Get contiguous time bounds for sea ice time series

        Creates new time bounds [
            [01-01-current year, 01-07-current year],
            [01-07-current year, 01-01-next year],
        ]
        """

        dt_object = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
        start = datetime.datetime(
            year=dt_object.year,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        end = datetime.datetime(
            year=start.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        mid_of_year = datetime.datetime(
            year=dt_object.year,
            month=7,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        start_seconds = cftime.date2num(start, time_coord.units.name)
        end_seconds = cftime.date2num(end, time_coord.units.name)
        mid_of_year_seconds = cftime.date2num(mid_of_year, time_coord.units.name)
        new_bounds = np.array([
            [start_seconds, mid_of_year_seconds],
            [mid_of_year_seconds, end_seconds],
        ])
        return new_bounds
    
    def set_cell_methods(self, cube, hemisphere):
        """Set the correct cell methods."""
        cube.cell_methods = ()
        cube.add_cell_method(iris.coords.CellMethod('point', coords='time'))
        cube.add_cell_method(
            iris.coords.CellMethod('sum', coords='area', intervals=f'{hemisphere}ern hemisphere')
            )
        return cube
