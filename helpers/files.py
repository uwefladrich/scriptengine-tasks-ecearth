"""Helper module for handling files."""

import os
from pathlib import Path

import jinja2
from scriptengine.jinja import filters as j2filters


# Using https://stackoverflow.com/revisions/13197763/9
class ChangeDirectory:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = Path(new_path).expanduser()
        self.saved_path = Path.cwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def get_template(context, template):
    """get Jinja2 template file"""
    search_path = [".", "templates"]
    if "_se_cmd_cwd" in context:
        search_path.extend(
            [
                context["_se_cmd_cwd"],
                Path(context["_se_cmd_cwd"]) / "templates",
            ]
        )

    loader = jinja2.FileSystemLoader(search_path)
    environment = jinja2.Environment(loader=loader)
    for name, function in j2filters().items():
        environment.filters[name] = function
    return environment.get_template(template)
