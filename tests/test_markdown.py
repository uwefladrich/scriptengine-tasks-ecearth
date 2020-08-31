"""Tests for scriptengine/tasks/monitoring/markdown.py"""

from unittest.mock import patch, Mock
import os

import pytest
import iris
import yaml

from scriptengine.tasks.ecearth.monitoring.markdown import Markdown

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
