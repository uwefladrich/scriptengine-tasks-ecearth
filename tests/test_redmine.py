"""Tests for monitoring/redmine.py"""

from unittest.mock import Mock, patch

import jinja2.exceptions
import pytest
import redminelib
import redminelib.exceptions
import scriptengine.exceptions

from monitoring.redmine import Redmine, sanitize_anchor_name


def test_redmine_presentation_list(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "redmine.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    redmine_task = Redmine(init)
    test_sources = ["path.txt", {"path": "path.txt"}, "path.yml"]
    with patch.object(redmine_task, "log_warning") as mock:
        result = redmine_task.get_presentation_list(test_sources, str(tmp_path))
    mock.assert_called_with("Can not present diagnostic: File not found: path.yml")
    assert result == []


def test_redmine_connection_error(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "redmine.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    redmine_task = Redmine(init)
    redmine = redminelib.Redmine("https://www.invalid.url", key=init["api_key"])
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        redmine_task.get_issue,
        redmine,
        init["subject"],
    )


def test_redmine_auth_error(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "redmine.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    redmine_task = Redmine(init)
    redmine = redminelib.Redmine("https://dev.ec-earth.org/", key=init["api_key"])
    pytest.raises(
        scriptengine.exceptions.ScriptEngineTaskRunError,
        redmine_task.get_issue,
        redmine,
        init["subject"],
    )


def test_redmine_get_template(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "redmine.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    redmine_output = Redmine(init)
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        redmine_output.get_template(init, init["template"])


class MockTemplateOrIssue:
    def __init__(self):
        self.globals = {}
        self.id = 0

    def render(self, **kwargs):
        return str(kwargs)

    def save(self):
        return None


def test_redmine_run(tmp_path):
    init = {
        "src": str(tmp_path),
        "local_dst": str(tmp_path),
        "template": str(tmp_path / "redmine.txt.j2"),
        "subject": "Test Issue",
        "api_key": "Invalid Key",
    }
    redmine_output = Redmine(init)
    redmine_output.get_presentation_list = Mock(return_value=[])
    mock_object = MockTemplateOrIssue()
    redmine_output.get_template = Mock(return_value=mock_object)
    redmine_output.get_issue = Mock(return_value=mock_object)
    with patch.object(redmine_output, "log_debug") as mock:
        redmine_output.run(init)
    mock.assert_called_with("Saving issue.")


def test_sanitize_anchor_name():
    test_string = "Precipitation - Evaporation (Annual Mean Climatology)"
    redmine_anchor = "Precipitation-Evaporation-Annual-Mean-Climatology"
    assert sanitize_anchor_name(test_string) == redmine_anchor
