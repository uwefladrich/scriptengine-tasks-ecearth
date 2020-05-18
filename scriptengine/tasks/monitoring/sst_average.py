"""Processing Task that calculates the global yearly SST average."""

from scriptengine.tasks.base import Task
from netCDF4 import Dataset
import numpy as np
import os, glob
import helpers.file_handling as file_handling
from datetime import datetime
import yaml

class SSTAverage(Task):
    def __init__(self, parameters):
        required = [
            "exp_id",
            "src",
            "dst",
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
        os.chdir(f"{self.src}")
        filepaths = [f"{self.src}/{filename}"
                     for filename in glob.glob(f"{self.exp_id}_1m_T_*.nc")]
        
        sst_array = np.array([])
        for path in filepaths:
            self.log_debug(f"Getting tos from {path}")
            data = Dataset(path, 'r')
            tos = data.variables["tos"]
            global_average = np.mean(tos[:])
            self.log_debug(f"Global average: {global_average}")
            sst_array = np.append(sst_array,global_average)
            data.close()
        
        average = np.mean(sst_array)
        self.log_debug(f"Yearly average: {average}")

        output = self.get_output_file()
        sst = output.variables["sst"]
        sst[:] = np.append(sst[:],average)
        output.close()


    def get_output_file(self):
        path = file_handling.filename(self.exp_id, self.mon_id, self.dst)
        try:
            file = Dataset(f"{path}.nc",'r+')
            return file
        except FileNotFoundError:
            file = Dataset(f"{path}.nc",'w')
            self.log_info("File was newly created. Setting up metadata.")
            
            file.createDimension('time',size=None)
            time = file.createVariable('time', 'i', ('time',))
            sst = file.createVariable('sst', 'f', ('time',))

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
            time_meta = { 
                'units': 's',
                'standard_name': 'time',
                'long_name': 'simulation year',
            }
            sst_meta = {
                'units': 'degree_Celsius',
                'standard_name': 'sea_surface_temperature',
                'long_name': 'yearly global SST average',
            }
            file.setncatts(metadata)
            time.setncatts(time_meta)
            sst.setncatts(sst_meta)
            return file