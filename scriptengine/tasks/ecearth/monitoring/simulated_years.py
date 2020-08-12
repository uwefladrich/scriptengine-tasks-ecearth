"""Processing Task that writes out the number of so far simulated years."""

from dateutil.relativedelta import relativedelta

from scriptengine.tasks.base.timing import timed_runner
from .scalar import Scalar

class SimulatedYears(Scalar):
    """SimulatedYears Processing Task"""
    def __init__(self, parameters):
        required = [
            "dst",
            "start",
            "end",
        ]
        super(Scalar, self).__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        dst = self.getarg('dst', context)
        start = self.getarg('start', context)
        end = self.getarg('end', context)
        self.log_info(f"Write simulated years to {dst}")

        value = relativedelta(end, start).years

        self.save(
            dst,
            title="Simulated Years",
            comment="Current number of simulated years.",
            data=value,
            type=self.diagnostic_type
        )
