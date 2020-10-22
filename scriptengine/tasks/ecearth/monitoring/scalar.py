"""Processing Task that writes out a generalized scalar diagnostic."""

import yaml

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError


class Scalar(Task):
    """Processing Task that writes out a generalized scalar diagnostic."""

    _required_arguments = ('title', 'value', 'dst', )

    def __init__(self, arguments=None):
        Scalar.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        title = self.getarg('title', context)
        dst = self.getarg('dst', context)

        self.log_info(f"Write scalar {title} to {dst}")

        value = self.getarg('value', context)
        comment = self.getarg('comment', context, default=None)

        self.save(dst, title=title, value=value, comment=comment)

    def save(self, dst, **kwargs):
        """Saves a scalar diagnostic in a YAML file."""
        self.log_debug(f"Saving scalar diagnostic to {dst}")
        filtered_dict = {k: v for k, v in kwargs.items() if v is not None}
        filtered_dict['diagnostic_type'] = 'scalar'
        if dst.endswith(".yml") or dst.endswith(".yaml"):
            with open(dst, 'w') as outfile:
                yaml.dump(filtered_dict, outfile, sort_keys=False)
        else:
            msg = (
                f"{dst} does not end in valid YAML file extension. "
                f"Diagnostic will not be saved."
            )
            self.log_error(msg)
            raise ScriptEngineTaskArgumentInvalidError(msg)
