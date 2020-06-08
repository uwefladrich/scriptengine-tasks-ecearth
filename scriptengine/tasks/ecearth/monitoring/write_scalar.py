"""Processing Task that writes out a given scalar value."""

import yaml

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render

class WriteScalar(Task):
    """WriteScalar Processing Task"""
    def __init__(self, parameters):
        required = [
            "long_name",
            "value",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.type = "scalar"

    def run(self, context):
        long_name = j2render(self.long_name, context)
        value = j2render(self.value, context)
        dst = j2render(self.dst, context)

        self.save(dst, long_name=long_name, data=value, type=self.type)

    def save(self, dst, **kwargs):
        """Saves a scalar diagnostic in a YAML file."""
        if dst.endswith(".yml") or dst.endswith(".yaml"):
            self.log_info(f"Saving Scalar diagnostic as {dst}")
            with open(dst, 'w') as outfile:
                yaml.dump(kwargs, outfile, sort_keys=False)
        else:
            self.log_warning((
                f"{dst} does not end in valid YAML file extension. "
                f"Diagnostic will not be saved."
            ))
