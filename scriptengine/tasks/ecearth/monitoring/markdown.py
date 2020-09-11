"""Presentation Task that saves Data and Plots to a Markdown File."""

import os

import jinja2
import yaml
import iris

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import filters as j2filters
from helpers.file_handling import ChangeDirectory
from helpers.presentation_objects import PresentationObject
from helpers.exceptions import PresentationException

class Markdown(Task):
    """Markdown Presentation Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "template",
        ]
        super().__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        sources = self.getarg('src', context)
        dst_folder = self.getarg('dst', context)
        template_path = self.getarg('template', context)
        self.log_info(f"Create Markdown report at {dst_folder}.")
        self.log_debug(f"Template: {template_path}, Source File(s): {sources}")

        presentation_list = self.get_presentation_list(sources, dst_folder)
        md_template = self.get_template(context, template_path)

        with ChangeDirectory(dst_folder):
            with open("./summary.md", 'w') as md_out:
                md_out.write(md_template.render(
                    presentation_list=presentation_list,
                ))

    def get_presentation_list(self, sources, dst_folder):
        """create a list of presentation objects"""
        self.log_debug("Getting list of presentation objects.")
        presentation_list = []
        for src in sources:
            try:
                try:
                    pres_object = PresentationObject(dst_folder, **src)
                except TypeError:
                    pres_object = PresentationObject(dst_folder, src)
                self.log_debug(f"Loading {pres_object.loader.diag_type} diagnostic from {pres_object.loader.path}.")
                presentation_list.append(pres_object.create_dict())
            except PresentationException as msg:
                self.log_warning(f"Can not present diagnostic: {msg}")
        return presentation_list

    def get_template(self, context, template_path):
        """get Jinja2 template file"""
        search_path = ['.', 'templates']
        if "_se_cmd_cwd" in context:
            search_path.extend([context["_se_cmd_cwd"],
                                os.path.join(context["_se_cmd_cwd"], "templates")])
        self.log_debug(f"Search path for template: {search_path}")

        loader = jinja2.FileSystemLoader(search_path)
        environment = jinja2.Environment(loader=loader)
        for name, function in j2filters().items():
            environment.filters[name] = function
        return environment.get_template(template_path)
