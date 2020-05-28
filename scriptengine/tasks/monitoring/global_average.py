"""Processing Task that calculates the global yearly average of a given extensive quantity."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render

import os, glob, ast

from netCDF4 import Dataset, num2date
import numpy as np

from datetime import datetime


class GlobalAverage(Task):
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "domain",
            "varname",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global average time series of the variable {self.varname}. "
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

        if not dst.endswith(".nc"):
            self.log_warning((
                f"{dst} does not end in valid netCDF file extension. "
                f"Diagnostic will not be treated, returning now."
            ))
            return
        
        try:
            src = ast.literal_eval(src)
        except ValueError:
            src = ast.literal_eval(f'"{src}"')

        self.log_info(f"Found {len(src)} files.")

        # Calculate cell areas
        try:
            domain_file = Dataset(domain,'r')
            cell_lengths = domain_file.variables["e1t"]
            cell_widths = domain_file.variables["e2t"]
        except (FileNotFoundError, KeyError):
            self.log_warning("Problem with domain file, aborting.")
            return
        cell_areas = np.multiply(cell_lengths[:], cell_widths[:])
        #print(type(cell_areas))

        global_avg_array = np.array([])
        left_bound = 1e+20
        right_bound = 0
        time_bound_weights = np.array([])

        var_metadata = {}
        for path in src:
            self.log_debug(f"Getting {varname} from {path}")
            nc_file = Dataset(path, 'r')

            nc_var = nc_file.variables[varname]
            global_average = np.ma.average(nc_var[:], weights=cell_areas)
            self.log_debug(f"Global average: {global_average}")
            
            global_avg_array = np.append(global_avg_array, global_average)

            bounds = nc_file.variables["time_counter_bounds"][:]
            time_interval = bounds[0][1] - bounds[0][0]
            time_bound_weights = np.append(time_bound_weights, time_interval)
            left_bound, right_bound = self.update_bounds(left_bound, right_bound, bounds)

            # access metadata of variable
            if not var_metadata:
                self.long_name = nc_var.long_name
                var_metadata["long_name"] = self.long_name
                var_metadata["standard_name"] = nc_var.standard_name
                var_metadata["missing_value"] = nc_var.missing_value
                var_metadata["units"] = nc_var.units

            nc_file.close()
        
        
        average = np.average(global_avg_array, weights=time_bound_weights)
        self.log_debug(f"Yearly average: {average}")
        time_value = np.mean([left_bound, right_bound])
        self.log_debug(f"new time value: {num2date(time_value, units='seconds since 1900-01-01 00:00:00')}")
        bound_values = [[left_bound, right_bound]]

        output = self.get_output_file(varname, dst)
        
        var_avg = output.variables[f"{varname}_avg"]
        tc = output.variables["time_counter"]
        tcb = output.variables["time_counter_bounds"]
        
        if self.monotonic_insert(tcb, bound_values):
            var_avg.setncatts(var_metadata)
            var_avg[:] = np.append(var_avg[:],average)
            tc[-1] = time_value
            tcb[-1] = bound_values
        else:
            self.log_warning(
                (f"Inserting time step would lead to "
                 f"non-monotonic time axis. "
                 f"Discarding current time step.")               
            )            
        
        output.close()


    def get_output_file(self, varname, dst):            
        try:
            file = Dataset(dst,'r+')
            file.set_auto_mask(False)
            return file
        except FileNotFoundError:
            file = Dataset(dst,'w')
            file.set_auto_mask(False)
            self.log_info("File was newly created. Setting up metadata.")
                       
            file.createDimension('time_counter', size=None)
            file.createDimension('axis_nbounds', size=2)
            tc = file.createVariable('time_counter', 'i8', ('time_counter',))
            tcb = file.createVariable('time_counter_bounds', 'i8', ('time_counter','axis_nbounds',))
            nc_avg = file.createVariable(f'{varname}_avg', 'f', ('time_counter',))

            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            metadata = {
                'title': f'{self.long_name.title()} (Global Average Time Series)',
                'source': 'EC-Earth 4',
                'history': dt_string + ': Creation',
                'comment': self.comment,
                'type': self.type,
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
        new_bounds_left = new_bounds.data[0][0] 
        new_bounds_right = new_bounds.data[0][1]
        if new_bounds_left < left_bound:
            self.log_debug(f"Updating left time bound to {new_bounds_left}")
            left_bound = new_bounds_left
        if new_bounds_right > right_bound:
            self.log_debug(f"Updating right time bound to {new_bounds_right}")
            right_bound = new_bounds_right
        return left_bound, right_bound

    def monotonic_insert(self, old_bounds, new_bounds):
        try:
            if old_bounds[-1][-1] > new_bounds[0][0]:
                return False
            else:
                return True
        except IndexError:
            return True