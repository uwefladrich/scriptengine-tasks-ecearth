"""Processing Task that writes out the number of so far simulated years."""

from dateutil.relativedelta import relativedelta

from scriptengine.tasks.base.timing import timed_runner
from .scalar import Scalar

class SimulatedyearsRteScalar(Scalar):
    """SimulatedyearsRteScalar Processing Task"""
    def __init__(self, parameters):
        super().__init__(
            parameters={**parameters, 'value': None, 'title': None},
            required_parameters=['start', 'end']
            )

    @timed_runner
    def run(self, context):
        dst = self.getarg('dst', context)
        start = self.getarg('start', context)
        end = self.getarg('end', context)
        self.log_info(f"Write simulated years to {dst}")

        self.value = relativedelta(end, start).years
        self.title = "Simulated Years"

        self.save(
            dst,
            title=self.title,
            comment="Current number of simulated years.",
            value=self.value,
        )
