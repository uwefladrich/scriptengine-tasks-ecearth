"""Processing Task that writes out the current leg number."""
from .write_scalar import WriteScalar
import yaml
import os
from scriptengine.jinja import render as j2render

class SimulatedLegs(WriteScalar):
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.long_name = "Simulated Legs"
        self.description = "Current leg number of EC-Earth run."
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src},{self.dst})"
        )

    def run(self, context):
        src = j2render(self.src, context)
        dst = j2render(self.dst, context)

        value = self.count_leg_folders(src)

        self.save(
            dst,
            name=self.long_name,
            description=self.description,
            data=value,
        )

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
    
    def count_leg_folders(self, src):
        """
        Get leg number by counting leg folders in rundir/output.
        """
        return len(next(os.walk(f"{src}/output"))[1])

