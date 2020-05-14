"""Processing Task that writes out the current leg number."""

from scriptengine.tasks.base import Task
import yaml
#from ....helpers import file_handling

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
            "description": self. description,
            "data": self.get_leg_number(),
        }
        convert_to_yaml(diagnostic,self.dst)
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


def filename(diagnostic, destination):
    """Creates the file name for a diagnostic dictionary."""
    
    if "exp_id" in diagnostic:
        exp_id = diagnostic["exp_id"]
    else:
        exp_id = "exp_id-not-given"
    
    if "mon_id" in diagnostic:
        mon_id = "-".join(diagnostic["mon_id"].split())
    else:
        mon_id = "mon_id-not-given"
    
    return f"{destination}/{exp_id}-{mon_id}"
    

def convert_to_yaml(diagnostic, destination):
    """Converts a diagnostic dictionary to a YAML file."""
    with open(f"{filename(diagnostic, destination)}.yml", 'w') as outfile:
        yaml.dump(diagnostic, outfile, sort_keys=False)