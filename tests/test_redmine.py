"""Tests for scriptengine/tasks/monitoring/redmine.py"""

from unittest.mock import patch, Mock

import pytest
import iris
import yaml

from scriptengine.tasks.ecearth.monitoring.redmine import Redmine

class MockTemplate:
    def render(self, **kwargs):
        return "string"

def test_invalid_key(tmpdir):
    init = {
        "src": str(tmpdir),
        "local_dst": str(tmpdir),
        "template": str(tmpdir) + "/redmine_template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_output = Redmine(init)
    redmine_output.get_presentation_list = Mock(return_value=None)
    mock_template = MockTemplate()
    redmine_output.get_template = Mock(return_value=mock_template)
    with patch.object(redmine_output, 'log_warning') as mock:
       redmine_output.run(init)
    mock.assert_called_with("Could not log in to Redmine server (AuthError)")
