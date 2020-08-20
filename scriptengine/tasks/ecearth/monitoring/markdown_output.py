"""Presentation Task that saves Data and Plots to a Markdown File."""

import os

import jinja2
import yaml
import iris

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import filters as j2filters
from helpers.file_handling import ChangeDirectory
from helpers.presentation_objects import make_time_series, make_static_map, make_dynamic_map
from helpers.exceptions import InvalidMapTypeException

class MarkdownOutput(Task):
    """MarkdownOutput Presentation Task"""
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
        presentation_list = []
        for src in sources:
            presentation_list.append(self.presentation_object(src, dst_folder))
        # remove None objects from list and return
        return [item for item in presentation_list if item]

    def presentation_object(self, src, dst_folder):
        """
        create a presentation object from an input path

        returns None
        - if the provided path is invalid
        - if the diagnostic_type or map_type is invalid

        otherwise returns a dictionary containing the keys:
        - title
        - comment
        - presentation_type (text or image)
        - for text objects: data
        - for image objects: path
        """
        if src.endswith('.yml') or src.endswith('.yaml'):
            try:
                with open(src) as yml_file:
                    loaded_dict = yaml.load(yml_file, Loader=yaml.FullLoader)
                return {'presentation_type': 'text', **loaded_dict}
            except FileNotFoundError:
                self.log_warning(f"File not found! Ignoring {src}")
                return None
    
        if src.endswith('.nc'):
            try:
                loaded_cube = iris.load_cube(src)
            except OSError:
                self.log_warning(f"File not found! Ignoring {src}")
                return None
            if loaded_cube.attributes["type"] == "time series":
                self.log_debug(f"Loading time series diagnostic {src}")
                return {'presentation_type': 'image', **make_time_series(src, dst_folder, loaded_cube)}
            if loaded_cube.attributes["type"] == "static map":
                self.log_debug(f"Loading static map diagnostic {src}")
                try:
                    map_plot_dict = make_static_map(src, dst_folder, loaded_cube)
                except InvalidMapTypeException as msg:
                    self.log_warning(f"Invalid Map Type {msg}")
                    return None
                return {'presentation_type': 'image', **map_plot_dict}
            if loaded_cube.attributes["type"] == "dynamic map":
                self.log_debug(f"Loading dynamic map diagnostic {src}")
                try:
                    map_plot_dict = make_dynamic_map(src, dst_folder, loaded_cube)
                except InvalidMapTypeException as msg:
                    self.log_warning(f"Invalid Map Type {msg}")
                    return None
                return {'presentation_type': 'image', **map_plot_dict}
            self.log_warning(f"Invalid diagnostic type {loaded_cube.attributes['type']}")
            return None
    
        self.log_warning(f"Invalid file extension of {src}")
        return None

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
