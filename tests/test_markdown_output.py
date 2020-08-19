"""Tests for scriptengine/tasks/monitoring test_markdown_output.py"""

from unittest.mock import patch, Mock
import os

import pytest
import iris
import yaml

from scriptengine.tasks.ecearth.monitoring.markdown_output import MarkdownOutput

def mock_pres_object(value_1, value_2):
    if value_1 == 1:
        return value_2
    return None

def test_markdown_output_full(tmpdir):
    init = {
        "src": [str(tmpdir) + "/test.yml"],
        "dst": str(tmpdir),
        "template": './docs/templates/monitoring.md.j2',
    }
    with open(init['src'][0], 'w') as file:
        yaml.dump(init, file)
    markdown_output = MarkdownOutput(init)

    markdown_output.run(init)
    assert os.path.isfile(init['dst'] + "/summary.md")

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

    with patch.object(markdown_output, 'log_warning') as mock:
        for src, msg in zip(init['src'], error_messages):
            markdown_output.presentation_object(src, init['dst'])
            mock.assert_called_with(msg)

def test_presentation_object_yaml(tmpdir):
    init = {
        "src": [str(tmpdir) + "/test.yml"],
        "dst": "",
        "template": "/.template.txt.j2",
    }
    with open(init['src'][0], 'w') as file:
        yaml.dump(init, file)
    markdown_output = MarkdownOutput(init)

    result = markdown_output.presentation_object(init['src'][0], init['dst'])
    assert result == {'presentation_type': 'text', **init}

def test_presentation_object_time_series(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "dst": "",
        "template": "/.template.txt.j2",
    }
    def mockreturn(src, dst_folder, loaded_cube):
        return {'src': src, 'dst_folder': dst_folder, 'name': loaded_cube.name()}
    markdown_output = MarkdownOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'time series'})
    iris.save(cube, init['src'][0])
    monkeypatch.setattr("helpers.presentation_objects.make_time_series.__code__", mockreturn.__code__)
    result = markdown_output.presentation_object(init['src'][0], init['dst'])
    assert result == {'presentation_type': 'image', **mockreturn(init['src'][0], init['dst'], cube)}

def test_presentation_object_static_map(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "dst": "",
        "template": "/.template.txt.j2",
    }
    def mockreturn(src, dst_folder, loaded_cube):
        return {'src': src, 'dst_folder': dst_folder, 'name': loaded_cube.name()}
    markdown_output = MarkdownOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'static map', 'map_type': 'invalid'})
    iris.save(cube, init['src'][0])
    result = markdown_output.presentation_object(init['src'][0], init['dst'])
    assert result is None

    cube = iris.cube.Cube([0], attributes={'type': 'static map', 'map_type': 'global ocean'})
    iris.save(cube, init['src'][0])
    monkeypatch.setattr("helpers.presentation_objects.make_static_map.__code__", mockreturn.__code__)
    result = markdown_output.presentation_object(init['src'][0], init['dst'])
    assert result == {'presentation_type': 'image', **mockreturn(init['src'][0], init['dst'], cube)}

def test_presentation_object_dynamic_map(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "dst": "",
        "template": "/.template.txt.j2",
    }
    def mockreturn(src, dst_folder, loaded_cube):
        return {'src': src, 'dst_folder': dst_folder, 'name': loaded_cube.name()}
    markdown_output = MarkdownOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'dynamic map', 'map_type': 'invalid'})
    iris.save(cube, init['src'][0])
    result = markdown_output.presentation_object(init['src'][0], init['dst'])
    assert result is None

    cube = iris.cube.Cube([0], attributes={'type': 'dynamic map', 'map_type': 'global ocean'})
    iris.save(cube, init['src'][0])
    monkeypatch.setattr("helpers.presentation_objects.make_dynamic_map.__code__", mockreturn.__code__)
    result = markdown_output.presentation_object(init['src'][0], init['dst'])
    assert result == {'presentation_type': 'image', **mockreturn(init['src'][0], init['dst'], cube)}

def test_presentation_object_invalid_diagnostic_type(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "dst": "",
        "template": "/.template.txt.j2",
    }
    markdown_output = MarkdownOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'invalid'})
    iris.save(cube, init['src'][0])
    with patch.object(markdown_output, 'log_warning') as mock:
        assert markdown_output.presentation_object(init['src'][0], init['dst']) is None
    mock.assert_called_with(f"Invalid diagnostic type {cube.attributes['type']}")

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
