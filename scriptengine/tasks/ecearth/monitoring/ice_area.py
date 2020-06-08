"""Processing Task that calculates the global sea ice area in one leg."""

import os
import ast

import iris
from iris.experimental.equalise_cubes import equalise_attributes
import numpy as np
import cf_units

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
from helpers.file_handling import get_month_from_src

class SeaIceArea(Task):
    """SeaIceArea Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "domain",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global Ice Area over one leg, "
                        f"separated into Northern and Southern Hemisphere. ")
        self.type = "time series"
        self.long_name = "Global Sea Ice Area"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src},{self.domain},{self.dst})"
        )

    def run(self, context):
        """run function of SeaIceArea Processing Task"""
        src = j2render(self.src, context)
        dst = j2render(self.dst, context)
        domain = j2render(self.domain, context)
        try:
            src = ast.literal_eval(src)
        except ValueError:
            src = ast.literal_eval(f'"{src}"')

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic can not be saved, returning now."
            ))
            return

        # Get March and September files from src
        try:
            mar = get_month_from_src("03", src)
            sep = get_month_from_src("09", src)
        except FileNotFoundError as error:
            self.log_warning((f"FileNotFoundError: {error}."
                              f"Diagnostic can not be created, returning now."))
            return

        month_cubes = iris.load([mar, sep], 'siconc')
        equalise_attributes(month_cubes) # 'timeStamp' and 'uuid' would cause ConcatenateError
        leg_cube = month_cubes.concatenate_cube()
        latitudes = np.broadcast_to(leg_cube.coord('latitude').points, leg_cube.shape)

        # Calculate cell areas
        domain_cfg = iris.load(domain)
        cell_areas = domain_cfg.extract('e1t')[0][0] * domain_cfg.extract('e2t')[0][0]
        cell_weights = np.broadcast_to(cell_areas.data, leg_cube.shape)

        # Treat main cube properties before extracting hemispheres
        time_aux = leg_cube.coord('time', dim_coords=False)
        leg_cube.remove_coord(time_aux)
        metadata = {
            'title': self.long_name.title(),
            'comment': self.comment,
            'type': self.type,
            'source': 'EC-Earth 4',
            'Conventions': 'CF-1.7',
            }
        metadata_to_discard = [
            'description',
            'interval_operation',
            'interval_write',
            'name',
            'online_operation',
            ]
        for key, value in metadata.items():
            leg_cube.attributes[key] = value
        for key in metadata_to_discard:
            leg_cube.attributes.pop(key, None)
        leg_cube.standard_name = "sea_ice_area"
        leg_cube.units = cf_units.Unit('m2')
        leg_cube.convert_units('1e6 km2')

        nh_cube = leg_cube.copy()
        sh_cube = leg_cube.copy()
        nh_cube.data = np.ma.masked_where(latitudes < 0, leg_cube.data)
        sh_cube.data = np.ma.masked_where(latitudes > 0, leg_cube.data)

        nh_weighted_sum = nh_cube.collapsed(
            ['latitude', 'longitude'],
            iris.analysis.SUM,
            weights=cell_weights,
            )
        sh_weighted_sum = sh_cube.collapsed(
            ['latitude', 'longitude'], 
            iris.analysis.SUM,
            weights=cell_weights,
            )
        nh_weighted_sum.long_name = self.long_name + " on Northern Hemisphere"
        sh_weighted_sum.long_name = self.long_name + " on Southern Hemisphere"
        nh_weighted_sum.var_name = 'siarean'
        sh_weighted_sum.var_name = 'siareas'

        self.save_cubes(nh_weighted_sum, sh_weighted_sum, dst)
    
    def save_cubes(self, new_siarean, new_siareas, dst):
        """save sea ice area cubes in netCDF file"""
        try:
            current_siarean = iris.load_cube(dst, 'siarean')
            current_siareas = iris.load_cube(dst, 'siareas')
            current_bounds = current_siarean.coord('time').bounds
            new_bounds = new_siarean.coord('time').bounds
            if current_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                siarean_list = iris.cube.CubeList([current_siarean, new_siarean])
                siareas_list = iris.cube.CubeList([current_siareas, new_siareas])
                siarean = siarean_list.concatenate_cube()
                siareas = siareas_list.concatenate_cube()
                siarea_global = iris.cube.CubeList([siarean, siareas])
                iris.save(siarea_global, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            siarea_global = iris.cube.CubeList([new_siarean, new_siareas])
            iris.save(siarea_global, dst)
        