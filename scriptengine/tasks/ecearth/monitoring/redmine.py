"""Presentation Task that uploads Data and Plots to the EC-Earth dev portal."""

import os

import redminelib
import redminelib.exceptions

import jinja2
import yaml
import iris

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import filters as j2filters
from helpers.presentation_objects import make_timeseries, make_map, make_temporalmap
from helpers.exceptions import InvalidMapTypeException

class Redmine(Task):
    """Redmine Presentation Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "local_dst",
            "subject",
            "template",
            "api_key",
        ]
        super().__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        sources = self.getarg('src', context)
        dst_folder = self.getarg('local_dst', context)
        issue_subject = self.getarg('subject', context)
        template_path = self.getarg('template', context)
        key = self.getarg('api_key', context)
        self.log_info(f"Create new issue '{issue_subject}'.")
        self.log_debug(f"Template: {template_path}, Source File(s): {sources}")

        presentation_list = self.get_presentation_list(sources, dst_folder)
        redmine_template = self.get_template(context, template_path)
        issue_description = redmine_template.render(presentation_list=presentation_list)

        url = 'https://dev.ec-earth.org'
        redmine = redminelib.Redmine(url, key=key)

        issue = self.get_issue(redmine, issue_subject)
        if issue is None:
            return

        self.log_info("Updating the issue.")

        issue.description = ""
        for line in issue_description:
            issue.description += line

        issue.uploads = []
        for item in presentation_list:
            if item['presentation_type'] == 'image':
                file_name = os.path.basename(item['path'])
                try:
                    for attachment in issue.attachments or []:
                        if attachment.filename == file_name:
                            redmine.attachment.delete(attachment.id)
                except redminelib.exceptions.ResourceNotFoundError:
                    pass
                issue.uploads.append({'filename': file_name, 'path': f"{dst_folder}/{file_name}"})
        issue.save()

    def get_presentation_list(self, sources, dst_folder):
        """create a list of presentation objects"""
        presentation_list = []
        for src in sources:
            presentation_list.append(self.presentation_object(src, dst_folder))
        # remove None objects from list
        presentation_list = [item for item in presentation_list if item]
        return presentation_list

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
            if loaded_cube.attributes["diagnostic_type"] == "time series":
                self.log_debug(f"Loading time series diagnostic {src}")
                return {'presentation_type': 'image', **make_timeseries(src, dst_folder, loaded_cube)}
            if loaded_cube.attributes["diagnostic_type"] == "map":
                self.log_debug(f"Loading map diagnostic {src}")
                try:
                    map_plot_dict = make_map(src, dst_folder, loaded_cube)
                except InvalidMapTypeException as msg:
                    self.log_warning(f"Invalid Map Type {msg}")
                    return None
                return {'presentation_type': 'image', **map_plot_dict}
            if loaded_cube.attributes["diagnostic_type"] == "temporal map":
                self.log_debug(f"Loading temporal map diagnostic {src}")
                try:
                    map_plot_dict = make_temporalmap(src, dst_folder, loaded_cube)
                except InvalidMapTypeException as msg:
                    self.log_warning(f"Invalid Map Type {msg}")
                    return None
                return {'presentation_type': 'image', **map_plot_dict}
            self.log_warning(f"Invalid diagnostic type {loaded_cube.attributes['diagnostic_type']}")
            return None

        self.log_warning(f"Invalid file extension of {src}")
        return None

    def get_template(self, context, template):
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
        return environment.get_template(template)

    def get_issue(self, redmine, issue_subject):
        """Connect to Redmine server, find and return issue corresponding to the experiment ID"""

        project_identifier = 'ec-earth-experiments'
        tracker_name = 'Experiment'

        try:
            tracker = next(t for t in redmine.tracker.all() if t.name == tracker_name)
        except redminelib.exceptions.AuthError:
            self.log_warning('Could not log in to Redmine server (AuthError)')
            return
        except StopIteration:
            self.log_warning('Redmine tracker for EC-Earth experiments not found')
            return

        # Find issue or create if none exists; define issue's last leg
        for issue in redmine.issue.filter(project_id=project_identifier, tracker_id=tracker.id):
            if issue.subject == issue_subject:
                break
        else:
            issue = redmine.issue.new()
            issue.project_id = project_identifier
            issue.subject = issue_subject
            issue.tracker_id = tracker.id
            issue.is_private = False

        return issue
