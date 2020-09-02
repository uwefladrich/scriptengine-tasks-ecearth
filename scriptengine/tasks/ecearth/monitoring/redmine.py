"""Presentation Task that uploads Data and Plots to the EC-Earth dev portal."""

import os
import urllib.parse
import requests

import redminelib
import redminelib.exceptions

import jinja2
import yaml
import iris

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import filters as j2filters
from helpers.presentation_objects import PresentationObject
from helpers.exceptions import PresentationException
from helpers.file_handling import ChangeDirectory

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
        issue_subject = self.getarg('subject', context, parse_yaml=False)
        template_path = self.getarg('template', context)
        key = self.getarg('api_key', context)
        self.log_info(f"Create Redmine issue '{issue_subject}'.")
        self.log_debug(f"Template: {template_path}, Source File(s): {sources}")

        presentation_list = self.get_presentation_list(sources, dst_folder)
        redmine_template = self.get_template(context, template_path)
        redmine_template.globals['urlencode'] = urllib.parse.quote
        issue_description = redmine_template.render(presentation_list=presentation_list)
        with ChangeDirectory(dst_folder):
            with open("./issue_description.txt", 'w') as outfile:
                outfile.write(issue_description)

        url = 'https://dev.ec-earth.org'
        redmine = redminelib.Redmine(url, key=key)

        self.log_debug("Connecting to Redmine.")
        issue = self.get_issue(redmine, issue_subject)
        if issue is None:
            return

        self.log_debug("Updating the issue description.")
        issue.description = ""
        for line in issue_description:
            issue.description += line

        self.log_debug("Uploading attachments.")
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
        self.log_debug("Saving issue.")
        issue.save()

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
        tracker_identifier = 15 # 'Experiment'
        status_identifier = 14 # 'Ongoing'
        priority_identifier = 2 # 'Medium'

        # Find issue or create if none exists
        filtered_issues = redmine.issue.filter(project_id=project_identifier, tracker_id=tracker_identifier)
        try:
            for issue in filtered_issues:
                if issue.subject == issue_subject:
                    break
            else:
                issue = redmine.issue.new()
                issue.subject = issue_subject
                issue.project_id = project_identifier
                issue.tracker_id = tracker_identifier
                issue.status_id = status_identifier
                issue.priority_id = priority_identifier
                issue.assigned_to_id = redmine.auth().id
                issue.is_private = False
            return issue
        except redminelib.exceptions.AuthError:
            self.log_warning('Could not log in to Redmine server (AuthError)')
            return
        except requests.exceptions.ConnectionError:
            self.log_warning('Could not log in to Redmine server (ConnectionError)')
            return
