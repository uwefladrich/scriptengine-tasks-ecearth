"""Tests for scriptengine/tasks/monitoring/redmine.py"""

from unittest.mock import patch, Mock

import pytest
import iris
import yaml
import redminelib
import redminelib.exceptions
import jinja2.exceptions

from scriptengine.tasks.ecearth.monitoring.redmine import Redmine

def test_redmine_presentation_list(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/redmine_template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_task = Redmine(init)
    test_sources = [
        'path.txt',
        {'path': 'path.txt'},
        'path.yml'
    ]
    with patch.object(redmine_task, 'log_warning') as mock:
        result = redmine_task.get_presentation_list(test_sources, str(tmpdir))
    mock.assert_called_with("Can not present diagnostic: File not found! Ignoring path.yml")
    assert result == []

def test_redmine_connection_error(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/redmine_template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_task = Redmine(init)
    redmine = redminelib.Redmine('https://www.invalid.url', key=init['api_key'])
    with patch.object(redmine_task, 'log_warning') as mock:
       redmine_task.get_issue(redmine, init['subject'])
    mock.assert_called_with("Could not log in to Redmine server (ConnectionError)")

def test_redmine_auth_error(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/redmine_template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_task = Redmine(init)
    redmine = redminelib.Redmine('https://dev.ec-earth.org/', key=init['api_key'])
    with patch.object(redmine_task, 'log_warning') as mock:
       redmine_task.get_issue(redmine, init['subject'])
    mock.assert_called_with("Could not log in to Redmine server (AuthError)")

def test_redmine_get_template(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_output = Redmine(init)
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        redmine_output.get_template(init, init['template'])

class MockTemplateOrIssue:
    def __init__(self):
        self.globals = {}

    def render(self, **kwargs):
        return str(kwargs)
    
    def save(self):
        return None

def test_redmine_run(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_output = Redmine(init)
    redmine_output.get_presentation_list = Mock(return_value=[])
    mock_object = MockTemplateOrIssue()
    redmine_output.get_template = Mock(return_value=mock_object)
    redmine_output.get_issue = Mock(return_value=mock_object)
    with patch.object(redmine_output, 'log_debug') as mock:
       redmine_output.run(init)
    mock.assert_called_with("Saving issue.")
