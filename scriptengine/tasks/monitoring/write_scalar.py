"""Processing Task that writes out a given scalar value."""

from scriptengine.tasks.base import Task
import yaml
import os
import helpers.file_handling as file_handling
from scriptengine.jinja import render as j2render

class WriteScalar(Task):
    def __init__(self, parameters):
        required = [
            "name",
            "value",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.mon_id = "write scalar"
        #TODO: Description?
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.name},{self.value},{self.dst})"
        )

    def run(self, context):
        self.mon_id = f"{j2render(self.name, context)}"
        self.value = j2render(self.value, context)
        self.dst = j2render(self.dst, context)

        diagnostic = {
            "mon_id": self.mon_id,
            "data": self.value,
        }

        file_handling.convert_to_yaml(diagnostic,self.dst)