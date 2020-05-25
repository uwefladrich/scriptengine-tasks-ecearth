"""Processing Task that writes out a given scalar value."""

from scriptengine.tasks.base import Task
import yaml
import os
from scriptengine.jinja import render as j2render

class WriteScalar(Task):
    def __init__(self, parameters):
        required = [
            "name",
            "value",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        #TODO: Description?
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.name},{self.value},{self.dst})"
        )

    def run(self, context):
        name = j2render(self.name, context)
        value = j2render(self.value, context)
        dst = j2render(self.dst, context)

        self.save(dst, name=name, data=value)
    
    def save(self, dst, **kwargs):
        """Saves a scalar diagnostic in a YAML file."""
        with open(dst, 'w') as outfile:
            yaml.dump(kwargs, outfile, sort_keys=False)