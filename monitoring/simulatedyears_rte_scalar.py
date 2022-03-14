"""Processing Task that writes out the number of so far simulated years."""

from pathlib import Path

from dateutil.relativedelta import relativedelta
from scriptengine.tasks.core import timed_runner

from .scalar import Scalar


class SimulatedyearsRteScalar(Scalar):
    """SimulatedyearsRteScalar Processing Task"""

    _required_arguments = (
        "start",
        "end",
        "dst",
    )

    def __init__(self, arguments=None):
        SimulatedyearsRteScalar.check_arguments(arguments)
        super().__init__({**arguments, "value": None, "title": None})

    @timed_runner
    def run(self, context):
        dst = Path(self.getarg("dst", context))
        start = self.getarg("start", context)
        end = self.getarg("end", context)
        self.log_info(f"Write simulated years to {dst}")

        self.value = relativedelta(end, start).years
        self.title = "Simulated Years"

        self.save(
            dst,
            title=self.title,
            comment="Current number of simulated years.",
            value=self.value,
        )
