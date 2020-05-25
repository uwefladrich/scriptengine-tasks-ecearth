"""Processing Task that writes out the number of so far simulated years."""
from .write_scalar import WriteScalar
import os
from scriptengine.jinja import render as j2render
from dateutil.relativedelta import relativedelta
import datetime

class SimulatedYears(WriteScalar):
    def __init__(self, parameters):
        required = [
            "dst",
            "start",
            "end",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.long_name = "Simulated Years"
        self.description = "Current number of simulated years."
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.dst},{self.start},{self.end})"
        )

    def run(self, context):
        format_str = "%Y-%m-%d"

        dst = j2render(self.dst, context)
        start = j2render(self.start, context)
        end = j2render(self.end, context)
        start = datetime.datetime.strptime(start, format_str)
        end = datetime.datetime.strptime(end, format_str)
        
        value = relativedelta(end, start).years

        self.save(
            dst,
            name=self.long_name,
            description=self.description,
            data=value,
        )

