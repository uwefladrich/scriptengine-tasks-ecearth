"""Processing Task that writes out a generalized scalar diagnostic."""

from pathlib import Path

import yaml
from scriptengine.exceptions import ScriptEngineTaskArgumentInvalidError
from scriptengine.tasks.core import Task, timed_runner


class Scalar(Task):
    """Processing Task that writes out a generalized scalar diagnostic."""

    _required_arguments = (
        "title",
        "value",
        "dst",
    )

    def __init__(self, arguments=None):
        Scalar.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        title = self.getarg("title", context)
        dst = Path(self.getarg("dst", context))

        self.log_info(f"Write scalar {title} to {dst}")

        value = self.getarg("value", context)
        comment = self.getarg("comment", context, default=None)

        self.save(dst, title=title, value=value, comment=comment)

    def save(self, dst, **kwargs):
        """Saves a scalar diagnostic in a YAML file."""
        self.log_debug(f"Saving scalar diagnostic to {dst}")
        filtered_dict = {k: v for k, v in kwargs.items() if v is not None}
        filtered_dict["diagnostic_type"] = "scalar"
        if dst.suffix in (".yml", ".yaml"):
            with open(dst, "w") as outfile:
                yaml.dump(filtered_dict, outfile, sort_keys=False)
        else:
            self.log_error(f"Invalid YAML extension in dst '{dst}'")
            raise ScriptEngineTaskArgumentInvalidError()
