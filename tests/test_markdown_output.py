"""Tests for scriptengine/tasks/monitoring test_markdown_output.py"""

from unittest.mock import patch, Mock

from scriptengine.tasks.ecearth.monitoring.markdown_output import MarkdownOutput

def mock_pres_object(value_1, value_2):
    if value_1 == 1:
        return value_2
    return None

def test_presentation_object_file_extension():
    init = {
        "src": ["test.yml", "test.nc", "test.txt"],
        "dst": "",
        "template": "/.template.txt.j2",
    }
    error_messages = [
        f"File not found! Ignoring {init['src'][0]}",
        f"File not found! Ignoring {init['src'][1]}",
        f"Invalid file extension of {init['src'][2]}",
    ]
    markdown_output = MarkdownOutput(init)

    with patch.object(markdown_output, 'log_error') as mock:
        for src, msg in zip(init['src'], error_messages):
            markdown_output.presentation_object(src, init['dst'])
            mock.assert_called_with(msg)

def test_presentation_list(tmpdir):
    init = {
        "src": [0, 1],
        "dst": str(tmpdir),
        "template": str(tmpdir) + "/template.txt.j2",
    }
    markdown_output = MarkdownOutput(init)
    markdown_output.presentation_object = Mock(side_effect=mock_pres_object)
    result = markdown_output.get_presentation_list(init['src'], init['dst'])
    assert result == [init['dst']]
