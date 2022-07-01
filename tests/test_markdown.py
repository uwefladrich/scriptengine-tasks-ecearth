"""Tests for monitoring/markdown.py"""

from pathlib import Path
from unittest.mock import patch

import yaml

from monitoring.markdown import Markdown


def test_markdown_output_full(tmp_path):
    init = {
        "src": [str(tmp_path / "test.yml")],
        "dst": str(tmp_path),
        "template": "./docs/templates/markdown.md.j2",
    }
    with open(init["src"][0], "w") as file:
        yaml.dump(init, file)
    markdown_output = Markdown(init)

    markdown_output.run(init)
    dst_path = Path(init["dst"]) / "summary.md"
    assert dst_path.is_file()


def test_markdown_presentation_list(tmp_path):
    init = {
        "src": [str(tmp_path / "test.yml")],
        "dst": str(tmp_path),
        "template": "./docs/templates/markdown.md.j2",
    }
    markdown = Markdown(init)
    test_sources = ["path.txt", {"path": "path.txt"}, "path.yml"]
    with patch.object(markdown, "log_warning") as mock:
        result = markdown.get_presentation_list(test_sources, str(tmp_path))
    mock.assert_called_with("Can not present diagnostic: File not found: path.yml")
    assert result == []
