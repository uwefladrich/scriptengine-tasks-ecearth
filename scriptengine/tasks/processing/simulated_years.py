"""Processing Task that writes out the current leg number."""

from scriptengine.tasks.base import Task
import yaml
import helpers.file_handling as file_handling

class SimulatedYears(Task):
    def __init__(self, parameters):
        required = [
            "exp_id",
            "src",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.mon_id = "simulated years"
        self.description = "Current leg number of EC-Earth run."
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.exp_id},{self.src},{self.dst})"
        )

    def run(self, context):
        diagnostic = {
            "exp_id": self.exp_id,
            "mon_id": self.mon_id,
            "description": self.description,
            "data": self.get_leg_number(),
        }
        file_handling.convert_to_yaml(diagnostic,self.dst)
        pass

    def get_leg_number(self):
        with open(f"{self.src}/leginfo.yml", 'r') as file:
            leg_info = yaml.load(file, Loader=yaml.FullLoader)
        try:
            leg_number = leg_info["config"]["schedule"]["leg"]["num"]
        except:
            self.log_warning("Leg number not found!")
            leg_number = -1
        return leg_number

