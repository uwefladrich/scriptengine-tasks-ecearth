"""Processing Task that calculates the global yearly SST average."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
import helpers.file_handling as file_handling

import os, glob, ast

from netCDF4 import Dataset, num2date
import numpy as np

from datetime import datetime


class SSTAverage(Task):
    def __init__(self, parameters):
        required = [
            "exp_id",
            "src",
            "dst",
        #    "var",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.mon_id = "SST average"
        self.description = "Yearly global average of the Sea Surface Temperature over time."
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.exp_id},{self.src},{self.dst})"
        )

    def run(self, context):
#        os.chdir(f"{self.src}")
#        filepaths = [f"{self.src}/{filename}"
#                     for filename in glob.glob(f"{self.exp_id}_1m_T_*.nc")]
        self.src = j2render(self.src, context)
        path_list = ast.literal_eval(self.src)

        sst_array = np.array([])
        left_bound = 1e+20
        right_bound = 0
        for path in path_list:
            self.log_debug(f"Getting tos from {path}")
            t_file = Dataset(path, 'r')
            tos = t_file.variables["tos"]
            global_average = np.mean(tos[:])
            self.log_debug(f"Global average: {global_average}")
            sst_array = np.append(sst_array,global_average)
            bounds = t_file.variables["time_counter_bounds"]
            left_bound, right_bound = self.update_bounds(left_bound, right_bound, bounds)
            t_file.close()
        
        average = np.mean(sst_array)
        self.log_debug(f"Yearly average: {average}")
        time_value = int(np.mean([left_bound, right_bound]))
        self.log_debug(f"new time value: {num2date(time_value, units='seconds since 1900-01-01 00:00:00')}")
        bound_values = [[left_bound, right_bound]]

        output = self.get_output_file(context)
        sst = output.variables["sst_avg"]
        tc = output.variables["time_counter"]
        tcb = output.variables["time_counter_bounds"]
        sst[:] = np.append(sst[:],average)
        tc[-1] = time_value
        tcb[-1] = bound_values
        
        output.close()

    def get_output_file(self, context):
        exp_id = j2render(self.exp_id, context)
        path = file_handling.filename(exp_id, self.mon_id, self.dst)
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
            sst_avg = file.createVariable('sst_avg', 'f', ('time_counter',))

            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            metadata = {
                'title': self.mon_id,
                'institution': 'SMHI',
                'source': 'EC-Earth 4',
                'history': dt_string + ': Creation',
                'references': '?',
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
            sst_meta = {
                'units': 'degree_Celsius',
                'standard_name': 'sea_surface_temperature',
                'long_name': 'yearly global SST average',
            }
            file.setncatts(metadata)
            tc.setncatts(tc_meta)
            tcb.setncatts(tcb_meta)
            sst_avg.setncatts(sst_meta)
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