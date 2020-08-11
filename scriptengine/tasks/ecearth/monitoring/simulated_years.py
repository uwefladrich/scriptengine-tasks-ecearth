"""Processing Task that writes out the number of so far simulated years."""

from dateutil.relativedelta import relativedelta

from .write_scalar import WriteScalar
from scriptengine.tasks.base.timing import timed_runner

class SimulatedYears(WriteScalar):
    """SimulatedYears Processing Task"""
    def __init__(self, parameters):
        required = [
            "dst",
            "start",
            "end",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.title = "Simulated Years"
        self.comment = "Current number of simulated years."
        self.type = "scalar"

    @timed_runner
    def run(self, context):
        dst = self.getarg('dst', context)
        start = self.getarg('start', context)
        end = self.getarg('end', context)
        self.log_info(f"Write simulated years to {dst}")

        value = relativedelta(end, start).years

        self.save(
            dst,
            title=self.title,
            comment=self.comment,
            data=value,
            type=self.type,
        )
