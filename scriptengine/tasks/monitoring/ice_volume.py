"""Processing Task that calculates the global ice volume in one leg."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render

import os, glob, ast

from netCDF4 import Dataset, num2date
import numpy as np

from datetime import datetime


class IceVolume(Task):
    def __init__(self, parameters):
        required = [
            "src",
            "domain",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.comment = (f"Global Ice Volume over one leg, "
                        f"separated into Northern and Southern Hemisphere. ")
        self.type = "time series"
        self.long_name = "Global Sea Ice Volume"
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src},{self.dst})"
        )

    def run(self, context):
        src = j2render(self.src, context)
        dst = j2render(self.dst, context)
        domain = j2render(self.domain, context)

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
        except:
            self.log_warning("Problem with domain file, aborting.")
            return

        cell_areas = np.multiply(cell_lengths[:], cell_widths[:])

        sivolu_nh_array = np.array([])
        sivolu_sh_array = np.array([])
        bounds_array = np.array([])
        left_bound = 1e+20
        right_bound = 0

        var_metadata = {}

        for path in src:
            self.log_debug(f"Getting sivolu from {path}")
            nc_file = Dataset(path, 'r')
            sivolu_per_area = nc_file.variables[f"sivolu"]
            sivolu = np.multiply(sivolu_per_area[:], cell_areas)
            lat_amount = sivolu.shape[1]
            lats = np.linspace(-90,90,lat_amount)
            sivolu_nh = sivolu[:, lats>0, :]
            sivolu_sh = sivolu[:, lats<=0, :]
            nh_sum = np.sum(sivolu_nh)
            sh_sum = np.sum(sivolu_sh)
            print(f"nh_sum = {nh_sum}, sh_sum = {sh_sum}")
            sivolu_nh_array = np.append(sivolu_nh_array, nh_sum)
            sivolu_sh_array = np.append(sivolu_sh_array, sh_sum)
            bounds = nc_file.variables["time_counter_bounds"][:]
            tcb_length = bounds[0][1] - bounds[0][0]
            bounds_array = np.append(bounds_array, tcb_length)
            left_bound, right_bound = self.update_bounds(left_bound, right_bound, bounds)

            nc_file.close()
        
        
        nh_average = np.average(sivolu_nh_array, weights=bounds_array)
        sh_average = np.average(sivolu_sh_array, weights=bounds_array)
        print(f"nh_average = {nh_average}, sh_average = {sh_average}")
        time_value = np.mean([left_bound, right_bound])
        self.log_debug(f"new time value: {num2date(time_value, units='seconds since 1900-01-01 00:00:00')}")
        bound_values = [[left_bound, right_bound]]

        output = self.get_output_file(dst)
        
        sivolu_nh = output.variables["total_sivolu_nh"]
        sivolu_sh = output.variables["total_sivolu_sh"]
        tc = output.variables["time_counter"]
        tcb = output.variables["time_counter_bounds"]
        
        if self.monotonic_insert(tcb, bound_values):
            tc[:] = np.append(tc[:],time_value)
            sivolu_nh[-1] = nh_average
            sivolu_sh[-1] = sh_average
            tcb[-1] = bound_values
        else:
            self.log_warning(
                (f"Inserting time step would lead to "
                 f"non-monotonic time axis. "
                 f"Discarding current time step.")               
            )            
        
        output.close()


    def get_output_file(self, dst):            
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
            sivolu_nh = file.createVariable(f'total_sivolu_nh', 'f', ('time_counter',))
            sivolu_sh = file.createVariable(f'total_sivolu_sh', 'f', ('time_counter',))

            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            metadata = {
                'title': f'{self.long_name.title()}',
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
            # access metadata of variable
            sh_metadata = {
                "long_name": self.long_name + " on Southern Hemisphere",
                "standard_name": "sea_ice_volume",
                "units": "m3",
            }
            nh_metadata = {
                "long_name": self.long_name + " on Northern Hemisphere",
                "standard_name": "sea_ice_volume",
                "units": "m3",
            }

            file.setncatts(metadata)
            tc.setncatts(tc_meta)
            tcb.setncatts(tcb_meta)
            sivolu_nh.setncatts(nh_metadata)
            sivolu_sh.setncatts(sh_metadata)
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

    def monotonic_insert(self, old_bounds, new_bounds):
        try:
            if old_bounds[-1][-1] > new_bounds[0][0]:
                return False
            else:
                return True
        except IndexError:
            return True