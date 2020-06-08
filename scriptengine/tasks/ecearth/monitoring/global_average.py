"""Processing Task that calculates the global yearly average of a given extensive quantity."""

import os
import ast

import numpy as np
import iris
from iris.experimental.equalise_cubes import equalise_attributes

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render

class GlobalAverage(Task):
    """GlobalAverage Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "domain",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global average time series of **{self.varname}**. "
                        f"Each data point represents the (spatial and temporal) "
                        f"average over one leg.")
        self.type = "time series"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src},{self.dst})"
        )

    def run(self, context):
        src = j2render(self.src, context)
        dst = j2render(self.dst, context)
        domain = j2render(self.domain, context)
        varname = j2render(self.varname, context)
        try:
            src = ast.literal_eval(src)
        except ValueError:
            src = ast.literal_eval(f'"{src}"')

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return

        # Calculate cell areas
        domain_cfg = iris.load(domain)
        cell_areas = domain_cfg.extract('e1t')[0][0] * domain_cfg.extract('e2t')[0][0]

        month_cubes = iris.load(src, varname)
        equalise_attributes(month_cubes) # 'timeStamp' and 'uuid' would cause ConcatenateError
        leg_cube = month_cubes.concatenate_cube()
        leg_cube.data = np.ma.masked_equal(leg_cube.data, 0) # land cells are not masked
        cell_weights = np.broadcast_to(cell_areas.data, leg_cube.shape)
        spatial_avg = leg_cube.collapsed(
            ['latitude', 'longitude'],
            iris.analysis.MEAN,
            weights=cell_weights,
            )

        time_aux = spatial_avg.coord('time', dim_coords=False)
        spatial_avg.remove_coord(time_aux)
        time_dim = spatial_avg.coord('time', dim_coords=True)
        month_lengths = np.array([bound[1] - bound[0] for bound in time_dim.bounds])

        ann_spatial_avg = spatial_avg.collapsed('time', iris.analysis.MEAN, weights=month_lengths)

        metadata = {
            'title': f'{ann_spatial_avg.long_name} (Global Average Time Series)',
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
            ann_spatial_avg.attributes[key] = value
        for key in metadata_to_discard:
            ann_spatial_avg.attributes.pop(key, None)

        self.save_cube(ann_spatial_avg, dst)


    def save_cube(self, ann_spatial_avg, dst):
        """save global average cubes in netCDF file"""
        try:
            old_diagnostic = iris.load_cube(dst)
            old_bounds = old_diagnostic.coord('time').bounds
            new_bounds = ann_spatial_avg.coord('time').bounds
            if old_bounds[-1][-1] > new_bounds[0][0]:
                self.log_warning("Inserting would lead to non-monotonic time axis. Aborting.")
            else:
                cubes = iris.cube.CubeList([old_diagnostic, ann_spatial_avg])
                diagnostic = cubes.merge_cube()
                iris.save(diagnostic, f"{dst}-copy.nc")
                os.remove(dst)
                os.rename(f"{dst}-copy.nc", dst)
        except OSError: # file does not exist yet.
            diagnostic = ann_spatial_avg
            iris.save(diagnostic, dst)
            return
        