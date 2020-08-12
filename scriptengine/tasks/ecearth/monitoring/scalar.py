"""Processing Task that writes out a generalized scalar diagnostic."""

import yaml

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner

class Scalar(Task):
    """Processing Task that writes out a generalized scalar diagnostic."""
    def __init__(self, parameters):
        required = [
            "title",
            "value",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
        self.type = "scalar"

    @timed_runner
    def run(self, context):
        title = self.getarg('title', context)
        value = self.getarg('value', context)
        dst = self.getarg('dst', context)
        comment = self.getarg('comment', context, default=None)
        self.log_info(f"Write scalar diagnostic to {dst}")

        self.save(dst, title=title, data=value, type=self.type, comment=comment)

    def save(self, dst, **kwargs):
        """Saves a scalar diagnostic in a YAML file."""
        filtered_dict = {k: v for k, v in kwargs.items() if v is not None}
        if dst.endswith(".yml") or dst.endswith(".yaml"):
            with open(dst, 'w') as outfile:
                yaml.dump(filtered_dict, outfile, sort_keys=False)
        else:
            self.log_warning((
                f"{dst} does not end in valid YAML file extension. "
                f"Diagnostic will not be saved."
            ))
