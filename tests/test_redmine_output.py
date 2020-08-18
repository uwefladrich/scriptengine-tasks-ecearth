"""Tests for scriptengine/tasks/monitoring test_markdown_output.py"""

from unittest.mock import patch, Mock

from scriptengine.tasks.ecearth.monitoring.redmine_output import RedmineOutput

class MockTemplate:
    def __init__(self):
        pass

    def render(self, **kwargs):
        pass

def mock_pres_object(value_1, value_2):
    if value_1 == 1:
        return value_2
    return None

def test_presentation_list(tmpdir):
    init = {
        "src": [0, 1],
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_output = RedmineOutput(init)
    redmine_output.presentation_object = Mock(side_effect=mock_pres_object)
    result = redmine_output.get_presentation_list(init['src'], init['local_dst'])
    assert result == [init['local_dst']]

def test_invalid_key(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_output = RedmineOutput(init)
    redmine_output.get_presentation_list = Mock(return_value=None)
    mock_template = MockTemplate()
    redmine_output.get_template = Mock(return_value=mock_template)
    with patch.object(redmine_output, 'log_error') as mock:
       redmine_output.run(init)
    mock.assert_called_with("Could not log in to Redmine server (AuthError)")

def test_presentation_object_file_extension():
    init = {
        "src": ["test.yml", "test.nc", "test.txt"],
        "local_dst": "",
        "template": "./template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    error_messages = [
        f"File not found! Ignoring {init['src'][0]}",
        f"File not found! Ignoring {init['src'][1]}",
        f"Invalid file extension of {init['src'][2]}",
    ]
    redmine_output = RedmineOutput(init)

    with patch.object(redmine_output, 'log_error') as mock:
        for src, msg in zip(init['src'], error_messages):
            redmine_output.presentation_object(src, init['local_dst'])
            mock.assert_called_with(msg)