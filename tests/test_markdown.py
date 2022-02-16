"""Tests for monitoring/markdown.py"""

from unittest.mock import patch
import os

import pytest
import yaml

from monitoring.markdown import Markdown

def test_markdown_output_full(tmpdir):
    init = {
        "src": [str(tmpdir) + "/test.yml"],
        "dst": str(tmpdir),
        "template": './docs/templates/markdown_template.md.j2',
    }
    with open(init['src'][0], 'w') as file:
        yaml.dump(init, file)
    markdown_output = Markdown(init)

    markdown_output.run(init)
    assert os.path.isfile(init['dst'] + "/summary.md")

def test_markdown_presentation_list(tmpdir):
    init = {
        "src": [str(tmpdir) + "/test.yml"],
        "dst": str(tmpdir),
        "template": './docs/templates/markdown_template.md.j2',
    }
    markdown = Markdown(init)
    test_sources = [
        'path.txt',
        {'path': 'path.txt'},
        'path.yml'
    ]
    with patch.object(markdown, 'log_warning') as mock:
        result = markdown.get_presentation_list(test_sources, str(tmpdir))
    mock.assert_called_with("Can not present diagnostic: File not found: path.yml")
    assert result == []
