"""Processing Task that writes out the current leg number."""

from scriptengine.tasks.base import Task
import yaml
import os
import helpers.file_handling as file_handling
from scriptengine.jinja import render as j2render

class SimulatedLegs(Task):
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.mon_id = "simulated legs"
        self.description = "Current leg number of EC-Earth run."
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src},{self.dst})"
        )

    def run(self, context):
        self.src = j2render(self.src, context)
        self.dst = j2render(self.dst, context)

        diagnostic = {
            "mon_id": self.mon_id,
            "description": self.description,
            "data": self.count_leg_folders(),
        }
        file_handling.convert_to_yaml(diagnostic,self.dst)
        pass

    def get_leg_number(self):
        """
        Alternative way to get leg number: Get leg number from leginfo.yml file.
        """
        with open(f"{self.src}/leginfo.yml", 'r') as file:
            leg_info = yaml.load(file, Loader=yaml.FullLoader)
        try:
            leg_number = leg_info["config"]["schedule"]["leg"]["num"]
        except:
            self.log_warning("Leg number not found!")
            leg_number = -1
        return leg_number
    
    def count_leg_folders(self):
        """
        Get leg number by counting leg folders in rundir/output.
        """
        return len(next(os.walk(f"{self.src}/output"))[1])

