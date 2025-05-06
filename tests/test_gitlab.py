"""Tests for monitoring/gitlab.py"""

from unittest.mock import Mock, patch

import gitlab
import jinja2.exceptions
import pytest
import scriptengine.exceptions

from monitoring.gitlab import Gitlab, create_anchor


def test_gitlab_presentation_list(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "gitlab.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    redmine_task = Gitlab(init)
    test_sources = ["path.txt", {"path": "path.txt"}, "path.yml"]
    with patch.object(redmine_task, "log_warning") as mock:
        result = redmine_task.get_presentation_list(test_sources, str(tmp_path))
    mock.assert_called_with("Can not present diagnostic: File not found: path.yml")
    assert result == []


def test_gitlab_connection_error(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "gitlab.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    gitlab_task = Gitlab(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        gitlab_task.get_project_and_issue,
        init["api_key"],
        init["subject"],
    )


def test_gitlab_auth_error(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "gitlab.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    gitlab_task = Gitlab(init)
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        gitlab_task.get_project_and_issue,
        init["api_key"],
        init["subject"],
    )


def test_gitlab_get_template(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "gitlab.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    gitlab_task = Gitlab(init)
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        gitlab_task.get_template(init, init["template"])


class MockTemplateOrIssue:
    def __init__(self):
        self.globals = {}
        self.web_url = ""

    def render(self, **kwargs):
        return str(kwargs)

    def save(self):
        return None

    def upload(self, file_name, filepath=""):
        return f"![{file_name}]({filepath})"


def test_gitlab_run(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "redmine.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    gitlab_task = Gitlab(init)
    gitlab_task.get_presentation_list = Mock(return_value=[])
    mock_object = MockTemplateOrIssue()
    gitlab_task.get_template = Mock(return_value=mock_object)
    gitlab_task.get_project_and_issue = Mock(return_value=(mock_object, mock_object))
    with patch.object(gitlab_task, "log_debug") as mock:
        gitlab_task.run(init)
    mock.assert_called_with("Saving issue.")


def test_create_anchor():
    test_string = "Precipitation - Evaporation (Annual Mean Climatology)"
    gitlab_anchor = "precipitation-evaporation-annual-mean-climatology"
    assert create_anchor(test_string) == gitlab_anchor
