"""Presentation Task that uploads Data and Plots to the EC-Earth dev portal."""

import re
import urllib.parse
from pathlib import Path

import jinja2
import redminelib
import redminelib.exceptions
import requests
from scriptengine.exceptions import ScriptEngineTaskRunError
from scriptengine.jinja import filters as j2filters
from scriptengine.tasks.core import Task, timed_runner

from helpers.exceptions import PresentationException
from helpers.presentation_objects import PresentationObject


class Redmine(Task):
    """Redmine Presentation Task"""

    _required_arguments = (
        "src",
        "local_dst",
        "subject",
        "template",
        "api_key",
    )

    def __init__(self, arguments=None):
        Redmine.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        sources = self.getarg("src", context)
        dst_folder = self.getarg("local_dst", context)
        issue_subject = self.getarg("subject", context, parse_yaml=False)
        template_path = self.getarg("template", context)
        key = self.getarg("api_key", context)
        self.log_info(f"Create Redmine issue '{issue_subject}'.")
        self.log_debug(f"Template: {template_path}, Source File(s): {sources}")

        presentation_list = self.get_presentation_list(sources, dst_folder)
        redmine_template = self.get_template(context, template_path)
        redmine_template.globals["urlencode"] = urllib.parse.quote

        server_url = "https://dev.ec-earth.org"
        redmine = redminelib.Redmine(server_url, key=key)

        self.log_debug("Connecting to Redmine.")
        issue = self.get_issue(redmine, issue_subject)

        self.log_debug("Updating the issue description.")
        # render the template and add as description
        issue_url = f"{server_url}/issues/{issue.id}"
        issue.description = redmine_template.render(
            presentation_list=presentation_list,
            issue_url=issue_url,
            create_anchor=sanitize_anchor_name,
        )

        self.log_debug("Uploading attachments.")
        issue.uploads = []
        for item in presentation_list:
            if item["presentation_type"] == "image":
                file_name = Path(item["path"]).name
                try:
                    for attachment in issue.attachments or []:
                        if attachment.filename == file_name:
                            redmine.attachment.delete(attachment.id)
                except redminelib.exceptions.ResourceNotFoundError:
                    pass
                issue.uploads.append(
                    {"filename": file_name, "path": f"{dst_folder}/{file_name}"}
                )
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
                self.log_debug(
                    f"Loading {pres_object.loader.diag_type} diagnostic from {pres_object.loader.path}."
                )
                presentation_list.append(pres_object.create_dict())
            except PresentationException as msg:
                self.log_warning(f"Can not present diagnostic: {msg}")
        return presentation_list

    def get_template(self, context, template):
        """get Jinja2 template file"""
        search_path = [".", "templates"]
        if "_se_cmd_cwd" in context:
            search_path.extend(
                [
                    context["_se_cmd_cwd"],
                    Path(context["_se_cmd_cwd"]) / "templates",
                ]
            )
        self.log_debug(f"Search path for template: {search_path}")

        loader = jinja2.FileSystemLoader(search_path)
        environment = jinja2.Environment(loader=loader)
        for name, function in j2filters().items():
            environment.filters[name] = function
        return environment.get_template(template)

    def get_issue(self, redmine, issue_subject):
        """Connect to Redmine server, find and return issue corresponding to the experiment ID"""

        project_identifier = "ec-earth-experiments"
        tracker_identifier = 15  # 'Experiment'
        status_identifier = 14  # 'Ongoing'
        priority_identifier = 2  # 'Medium'

        # Find issue or create if none exists
        filtered_issues = redmine.issue.filter(
            project_id=project_identifier, tracker_id=tracker_identifier
        )
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
                issue.save()  # save issue once to get a valid issue ID (it's 0 otherwise)
            return issue
        except (
            redminelib.exceptions.AuthError,
            requests.exceptions.ConnectionError,
        ) as e:
            msg = f"Could not log in to Redmine server ({e})"
            self.log_error(msg)
            raise ScriptEngineTaskRunError()


def sanitize_anchor_name(anchor: str) -> str:
    """
    create correct anchors for Redmine issue URLs

    This function is a Python-equivalent of the Ruby function sanitize_anchor_name()
    in the Redmine source code (app/helpers/application_helper.rb). It makes sure that
    1. non-word, non-whitespace characters are removed from the string
    2. whitespace characters are replaced with dashes, but existing dashes do not get duplicated.
    The logic is as close to the original as possible but is not Unicode aware (not natively supported by re package).
    """
    anchor = re.sub(r"[^a-zA-Z\s-]", "", anchor)
    anchor = re.sub(r"\s+(\-+\s*)?", "-", anchor)
    return anchor
