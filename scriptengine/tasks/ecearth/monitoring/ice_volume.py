"""Processing Task that calculates the global ice volume in one leg."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render

import os, glob, ast

from netCDF4 import Dataset, num2date
import numpy as np
import cf_units

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

        self.log_info(f"Found {len(src)} files.")

        # Get March and September files from src
        try:
            mar = self.get_month_from_src("03", src)
            sep = self.get_month_from_src("09", src)
        except FileNotFoundError as e:
            self.log_warning((f"FileNotFoundError: {e}."
                              f"Diagnostic can not be created, returning now."))
            return

        # Calculate cell areas
        try:
            domain_file = Dataset(domain,'r')
            cell_lengths = domain_file.variables["e1t"]
            cell_widths = domain_file.variables["e2t"]
        except (FileNotFoundError, KeyError) as e:
            self.log_warning((f"Problem with domain file, aborting."
                              f"Exception: {e}"))
            return   
        cell_areas = np.multiply(cell_lengths[:], cell_widths[:])

        # Initialization for the loop
        nh_sivolu_array = np.array([])
        sh_sivolu_array = np.array([])
        time_counter = []
        time_counter_bounds = []

        for month in [mar, sep]:
            self.log_debug(f"Getting 'sivolu' from {month}")
            nc_file = Dataset(month, 'r')

            volume_per_area = nc_file.variables["sivolu"][:]
            volume = np.multiply(volume_per_area, cell_areas)

            lat_amount = volume.shape[1] # nav_lat is second coordinate of sivolu variable
            lats = np.linspace(-90,90,lat_amount)
            nh_volume = volume[:, lats>0, :]
            sh_volume = volume[:, lats<=0, :]
            nh_sum = np.ma.sum(nh_volume)
            sh_sum = np.ma.sum(sh_volume)

            nh_sivolu_array = np.append(nh_sivolu_array, nh_sum)
            sh_sivolu_array = np.append(sh_sivolu_array, sh_sum)    

            value = nc_file.variables["time_counter"][:]
            bounds = nc_file.variables["time_counter_bounds"][:]

            time_counter_bounds.append(bounds)
            time_counter.append(value)

            nc_file.close()
        
        nh_sivolu_array = self.change_units(nh_sivolu_array)
        sh_sivolu_array = self.change_units(sh_sivolu_array)

        output = self.get_output_file(dst)
        
        total_nh_volume = output.variables["total_nh_volume"]
        total_sh_volume = output.variables["total_sh_volume"]
        tc = output.variables["time_counter"]
        tcb = output.variables["time_counter_bounds"]

        
        if self.monotonic_insert(tcb, time_counter_bounds[0]):
            tc[:] = np.append(tc[:],time_counter)
            total_nh_volume[-2] = nh_sivolu_array[0]
            total_nh_volume[-1] = nh_sivolu_array[1]
            total_sh_volume[-2] = sh_sivolu_array[0]
            total_sh_volume[-1] = sh_sivolu_array[1]
            tcb[-2] = time_counter_bounds[0]
            tcb[-1] = time_counter_bounds[1]
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
            tc = file.createVariable('time_counter', 'd', ('time_counter',))
            tcb = file.createVariable('time_counter_bounds', 'd', ('time_counter','axis_nbounds',))
            total_nh_volume = file.createVariable(f'total_nh_volume', 'f', ('time_counter',))
            total_sh_volume = file.createVariable(f'total_sh_volume', 'f', ('time_counter',))

            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            metadata = {
                'title': f'{self.long_name.title()}',
                'source': 'EC-Earth 4',
                'history': dt_string + ': Creation',
                'comment': self.comment,
                'type': self.type,
                'Conventions': 'CF-1.7',
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
                "units": "km3",
            }
            nh_metadata = {
                "long_name": self.long_name + " on Northern Hemisphere",
                "standard_name": "sea_ice_volume",
                "units": "km3",
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
    
    def get_month_from_src(self, month, path_list):
        for path in path_list:
            if path[-5:-3] == month:
                return path
        raise FileNotFoundError(f"Month {month} not found in {path_list}!")

    def change_units(self, arr):
        old_unit = cf_units.Unit('m3')
        target_unit = cf_units.Unit('km3')
        arr = old_unit.convert(arr, target_unit)
        return arr
        