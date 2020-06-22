"""Processing Task that writes out a given scalar value."""

import yaml

from scriptengine.tasks.base import Task

class WriteScalar(Task):
    """WriteScalar Processing Task"""
    def __init__(self, parameters):
        required = [
            "title",
            "value",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.type = "scalar"

    def run(self, context):
        title = self.getarg('title', context)
        value = self.getarg('value', context)
        dst = self.getarg('dst', context)
        self.log_info(f"Write scalar diagnostic to {dst}")

        self.save(dst, title=title, data=value, type=self.type)

    def save(self, dst, **kwargs):
        """Saves a scalar diagnostic in a YAML file."""
        if dst.endswith(".yml") or dst.endswith(".yaml"):
            with open(dst, 'w') as outfile:
                yaml.dump(kwargs, outfile, sort_keys=False)
        else:
            self.log_warning((
                f"{dst} does not end in valid YAML file extension. "
                f"Diagnostic will not be saved."
            ))
