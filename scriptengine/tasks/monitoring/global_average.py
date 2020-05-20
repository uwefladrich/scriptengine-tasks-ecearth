"""Processing Task that calculates the global yearly average of a given extensive quantity."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
import helpers.file_handling as file_handling

import os, glob, ast

from netCDF4 import Dataset, num2date
import numpy as np

from datetime import datetime


class GlobalAverage(Task):
    def __init__(self, parameters):
        required = [
            "exp_id",
            "src",
            "dst",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.mon_id = f"global average {self.varname}"
        self.description = (f"Global average of the variable {self.varname} "
                            f"per leg over time.")
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({j2render(self.exp_id,context)},{self.src},{self.dst})"
        )

    def run(self, context):
        self.src = j2render(self.src, context)
        self.dst = j2render(self.dst, context)
        self.exp_id = j2render(self.exp_id, context)
        try:
            self.src = ast.literal_eval(self.src)
        except ValueError:
            self.src = ast.literal_eval(f'"{self.src}"')

        self.log_info(f"Found {len(self.src)} files.")

        sst_array = np.array([])
        left_bound = 1e+20
        right_bound = 0

        var_metadata = {}
        for path in self.src:
            self.log_debug(f"Getting {self.varname} from {path}")
            nc_file = Dataset(path, 'r')
            nc_var = nc_file.variables[f"{self.varname}"]
            global_average = np.mean(nc_var[:])
            self.log_debug(f"Global average: {global_average}")
            sst_array = np.append(sst_array, global_average)
            bounds = nc_file.variables["time_counter_bounds"]
            left_bound, right_bound = self.update_bounds(left_bound, right_bound, bounds)

            # access metadata of variable
            if not var_metadata:
                var_metadata["standard_name"] = nc_var.standard_name
                var_metadata["long_name"] = nc_var.long_name
                var_metadata["missing_value"] = nc_var.missing_value
                var_metadata["units"] = nc_var.units

            nc_file.close()
        
        average = np.mean(sst_array)
        self.log_debug(f"Yearly average: {average}")
        time_value = np.mean([left_bound, right_bound])
        self.log_debug(f"new time value: {num2date(time_value, units='seconds since 1900-01-01 00:00:00')}")
        bound_values = [[left_bound, right_bound]]

        output = self.get_output_file()
        
        var_avg = output.variables[f"{self.varname}_avg"]
        tc = output.variables["time_counter"]
        tcb = output.variables["time_counter_bounds"]

        var_avg.setncatts(var_metadata)

        var_avg[:] = np.append(var_avg[:],average)
        tc[-1] = time_value
        tcb[-1] = bound_values
        
        output.close()

    def get_output_file(self):
        path = file_handling.filename(self.exp_id, self.mon_id, self.dst)
        try:
            file = Dataset(f"{path}.nc",'r+')
            return file
        except FileNotFoundError:
            file = Dataset(f"{path}.nc",'w')
            file.set_auto_mask(False)
            self.log_info("File was newly created. Setting up metadata.")
                       
            file.createDimension('time_counter', size=None)
            file.createDimension('axis_nbounds', size=2)
            tc = file.createVariable('time_counter', 'i8', ('time_counter',))
            tcb = file.createVariable('time_counter_bounds', 'i8', ('time_counter','axis_nbounds',))
            nc_avg = file.createVariable(f'{self.varname}_avg', 'f', ('time_counter',))

            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            metadata = {
                'title': f'Global Average of {self.varname}',
                'source': 'EC-Earth 4',
                'history': dt_string + ': Creation',
                'exp_id': self.exp_id,
                'description': self.description,
            #    'Conventions': 'CF-1.8',
            }
            tc_meta = { 
                'units': 'seconds since 1900-01-01 00:00:00',
                'standard_name': 'time',
                'long_name': 'time axis',
                'calendar': 'gregorian',
                'bounds': 'time_counter_bounds',
            }
            tcb_meta = {
                'long_name': 'bounds for time axis',
            }
            file.setncatts(metadata)
            tc.setncatts(tc_meta)
            tcb.setncatts(tcb_meta)
            return file
    
    def update_bounds(self, left_bound, right_bound, new_bounds):
        new_bounds_left = new_bounds[:].data[0][0] 
        new_bounds_right = new_bounds[:].data[0][1]
        if new_bounds_left < left_bound:
            self.log_debug(f"Updating left time bound to {new_bounds_left}")
            left_bound = new_bounds_left
        if new_bounds_right > right_bound:
            self.log_debug(f"Updating right time bound to {new_bounds_right}")
            right_bound = new_bounds_right
        return left_bound, right_bound