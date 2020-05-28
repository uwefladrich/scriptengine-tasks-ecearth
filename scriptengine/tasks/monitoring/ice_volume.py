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
            f"({self.src},{self.domain},{self.dst})"
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
        except (FileNotFoundError, KeyError):
            self.log_warning("Problem with domain file, aborting.")
            return
        cell_areas = np.multiply(cell_lengths[:], cell_widths[:])

        # Initialization for the loop
        nh_sivolu_array = np.array([])
        sh_sivolu_array = np.array([])
        time_bound_weights = np.array([])
        left_bound = 1e+20
        right_bound = 0

        for path in src:
            self.log_debug(f"Getting 'sivolu' from {path}")
            nc_file = Dataset(path, 'r')

            volume_per_area = nc_file.variables["sivolu"]
            volume = np.multiply(volume_per_area[:], cell_areas)

            lat_amount = volume.shape[1] # nav_lat is second coordinate of sivolu variable
            lats = np.linspace(-90,90,lat_amount)
            nh_volume = volume[:, lats>0, :]
            sh_volume = volume[:, lats<=0, :]
            nh_sum = np.ma.sum(nh_volume)
            sh_sum = np.ma.sum(sh_volume)

            nh_sivolu_array = np.append(nh_sivolu_array, nh_sum)
            sh_sivolu_array = np.append(sh_sivolu_array, sh_sum)    

            bounds = nc_file.variables["time_counter_bounds"][:]
            time_interval = bounds[0][1] - bounds[0][0]
            time_bound_weights = np.append(time_bound_weights, time_interval)
            left_bound, right_bound = self.update_bounds(left_bound, right_bound, bounds)

            nc_file.close()
        
        nh_average = np.average(nh_sivolu_array, weights=time_bound_weights)
        sh_average = np.average(sh_sivolu_array, weights=time_bound_weights)
        self.log_debug(f"nh_average = {nh_average}, sh_average = {sh_average}")
        
        time_value = np.mean([left_bound, right_bound])
        self.log_debug(f"new time value: {num2date(time_value, units='seconds since 1900-01-01 00:00:00')}")
        bound_values = [[left_bound, right_bound]]
        
        output = self.get_output_file(dst)
        
        total_nh_volume = output.variables["total_nh_volume"]
        total_sh_volume = output.variables["total_sh_volume"]
        tc = output.variables["time_counter"]
        tcb = output.variables["time_counter_bounds"]
        
        if self.monotonic_insert(tcb, bound_values):
            tc[:] = np.append(tc[:],time_value)
            total_nh_volume[-1] = nh_average
            total_sh_volume[-1] = sh_average
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
            total_nh_volume = file.createVariable(f'total_nh_volume', 'f', ('time_counter',))
            total_sh_volume = file.createVariable(f'total_sh_volume', 'f', ('time_counter',))

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
            total_nh_volume.setncatts(nh_metadata)
            total_sh_volume.setncatts(sh_metadata)
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