"""Presentation Task that uploads Data and Plots to the EC-Earth 4 Gitlab."""

import re
import urllib.parse
from pathlib import Path

import gitlab
import jinja2
import requests.exceptions
from scriptengine.exceptions import ScriptEngineTaskRunError
from scriptengine.jinja import filters as j2filters
from scriptengine.tasks.core import Task, timed_runner

from helpers.exceptions import PresentationException
from helpers.presentation_objects import PresentationObject


class Gitlab(Task):
    """Gitlab Presentation Task"""

    _required_arguments = (
        "src",
        "local_dst",
        "subject",
        "template",
        "api_key",
    )

    def __init__(self, arguments=None):
        Gitlab.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        sources = self.getarg("src", context)
        dst_folder = self.getarg("local_dst", context)
        issue_subject = self.getarg("subject", context, parse_yaml=False)
        template_path = self.getarg("template", context)
        key = self.getarg("api_key", context)
        self.log_info(f"Create Gitlab issue '{issue_subject}'.")
        self.log_debug(f"Template: {template_path}, Source File(s): {sources}")

        presentation_list = self.get_presentation_list(sources, dst_folder)
        gitlab_template = self.get_template(context, template_path)
        gitlab_template.globals["urlencode"] = urllib.parse.quote

        server_url = "https://gitlab.lrz.de"
        gl = gitlab.Gitlab(server_url, private_token=key)

        self.log_debug("Connecting to Gitlab.")

        project, issue = self.get_project_and_issue(gl, issue_subject)

        self.log_debug("Uploading attachments.")
        issue.uploads = []
        for item in presentation_list:
            if item["presentation_type"] == "image":
                file_name = Path(item["path"]).name
                upload = project.upload(file_name, filepath=f"{dst_folder}/{file_name}")
                item["image_link"] = upload[
                    "markdown"
                ]  # string of the form "![]()" generated by Gitlab

        # render the template and add as description
        self.log_debug("Updating the issue description.")
        issue.description = gitlab_template.render(
            presentation_list=presentation_list,
            issue_url=issue.web_url,
            create_anchor=create_anchor,
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

    def get_project_and_issue(self, gl, issue_subject):
        """Connect to Gitlab server, find and return correct issue and project based on user input"""

        project_id = 127437  # TODO update this
        try:
            project = gl.projects.get(project_id)
        except (
            gitlab.GitlabAuthenticationError,
            requests.exceptions.ConnectionError,
        ) as e:
            msg = f"Could not log in to Gitlab server ({e})"
            self.log_error(msg)
            raise ScriptEngineTaskRunError()

        # Find issue or create if none exists
        issues = project.issues.list()
        issue = next((issue for issue in issues if issue.title == issue_subject), None)
        if issue is None:
            issue = project.issues.create({"title": issue_subject})
            issue.save()
        return project, issue


def create_anchor(anchor: str) -> str:
    """
    create correct anchors for Gitlab issue URLs
    """
    anchor = re.sub(r"[^a-zA-Z\s-]", "", anchor)
    anchor = re.sub(r"\s+(\-+\s*)?", "-", anchor)
    anchor = anchor.lower()
    return anchor
