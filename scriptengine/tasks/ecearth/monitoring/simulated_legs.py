"""Processing Task that writes out the current leg number."""

import os
import yaml

from scriptengine.tasks.base.timing import timed_runner
from .scalar import Scalar

class SimulatedLegs(Scalar):
    """SimulatedLegs Processing Task."""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super(Scalar, self).__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        self.log_info(f"Write simulated legs to {dst}")

        value = self.count_leg_folders(src)

        self.save(
            dst,
            title="Simulated Legs",
            comment="Current amount of folders in output directory.",
            data=value,
            type=self.diagnostic_type,
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
        Get leg number by counting leg folders in src/output.
        If src does not contain output, count folders in src instead.
        """
        try:
            count = len(next(os.walk(src))[1])
        except StopIteration:
            self.log_warning(f"No folder 'output' in {src}. Counting folders in {src} instead.")
            count = len(next(os.walk(f"{src}/output"))[1])
        return count
