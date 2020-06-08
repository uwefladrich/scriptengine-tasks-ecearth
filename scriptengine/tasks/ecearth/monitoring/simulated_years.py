"""Processing Task that writes out the number of so far simulated years."""

import yaml # temporary until base class Task has getarg() function
from dateutil.relativedelta import relativedelta

from scriptengine.jinja import render as j2render
from .write_scalar import WriteScalar

class SimulatedYears(WriteScalar):
    """SimulatedYears Processing Task"""
    def __init__(self, parameters):
        required = [
            "dst",
            "start",
            "end",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.long_name = "Simulated Years"
        self.comment = "Current number of simulated years."
        self.type = "scalar"

    def run(self, context):
        dst = j2render(self.dst, context)
        rendered_start = j2render(self.start, context)
        rendered_end = j2render(self.end, context)

        try:
            start = yaml.full_load(rendered_start)
        except (yaml.parser.ParserError, yaml.constructor.ConstructorError):
            start = rendered_start
        try:
            end = yaml.full_load(rendered_end)
        except (yaml.parser.ParserError, yaml.constructor.ConstructorError):
            end = rendered_end

        value = relativedelta(end, start).years

        self.save(
            dst,
            long_name=self.long_name,
            comment=self.comment,
            data=value,
            type=self.type,
        )
