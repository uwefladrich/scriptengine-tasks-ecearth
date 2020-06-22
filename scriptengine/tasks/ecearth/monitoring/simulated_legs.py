"""Processing Task that writes out the current leg number."""

import os
import yaml

from .write_scalar import WriteScalar

class SimulatedLegs(WriteScalar):
    """SimulatedLegs Processing Task."""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.title = "Simulated Legs"
        self.comment = "Current amount of folders in output directory."
        self.type = "scalar"

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)

        value = self.count_leg_folders(src)

        self.save(
            dst,
            title=self.title,
            comment=self.comment,
            data=value,
            type=self.type,
        )

    def get_leg_number(self, src):
        """
        Alternative way to get leg number: Get leg number from leginfo.yml file.
        """
        with open(f"{src}/leginfo.yml", 'r') as file:
            leg_info = yaml.load(file, Loader=yaml.FullLoader)
        try:
            leg_number = leg_info["config"]["schedule"]["leg"]["num"]
        except (KeyError, TypeError):
            self.log_warning("Leg number not found!")
            leg_number = -1
        return leg_number

    def count_leg_folders(self, src):
        """
        Get leg number by counting leg folders in rundir/output.
        """
        return len(next(os.walk(f"{src}/output"))[1])
