"""Tests for scriptengine/tasks/monitoring test_redmine_output.py"""

from unittest.mock import patch, Mock

import pytest
import iris

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
    with patch.object(redmine_output, 'log_warning') as mock:
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

    with patch.object(redmine_output, 'log_warning') as mock:
        for src, msg in zip(init['src'], error_messages):
            redmine_output.presentation_object(src, init['local_dst'])
            mock.assert_called_with(msg)

def test_presentation_object_time_series(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "local_dst": "",
        "template": "./template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    def mockreturn(src, dst_folder, loaded_cube):
        return {'src': src, 'dst_folder': dst_folder, 'name': loaded_cube.name()}
    redmine_output = RedmineOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'time series'})
    iris.save(cube, init['src'][0])
    monkeypatch.setattr("helpers.presentation_objects.make_time_series.__code__", mockreturn.__code__)
    result = redmine_output.presentation_object(init['src'][0], init['local_dst'])
    assert result == {'presentation_type': 'image', **mockreturn(init['src'][0], init['local_dst'], cube)}

def test_presentation_object_static_map(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "local_dst": "",
        "template": "./template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    def mockreturn(src, dst_folder, loaded_cube):
        return {'src': src, 'dst_folder': dst_folder, 'name': loaded_cube.name()}
    redmine_output = RedmineOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'static map', 'map_type': 'invalid'})
    iris.save(cube, init['src'][0])
    result = redmine_output.presentation_object(init['src'][0], init['local_dst'])
    assert result is None

    cube = iris.cube.Cube([0], attributes={'type': 'static map', 'map_type': 'global ocean'})
    iris.save(cube, init['src'][0])
    monkeypatch.setattr("helpers.presentation_objects.make_static_map.__code__", mockreturn.__code__)
    result = redmine_output.presentation_object(init['src'][0], init['local_dst'])
    assert result == {'presentation_type': 'image', **mockreturn(init['src'][0], init['local_dst'], cube)}

def test_presentation_object_dynamic_map(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "local_dst": "",
        "template": "./template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    def mockreturn(src, dst_folder, loaded_cube):
        return {'src': src, 'dst_folder': dst_folder, 'name': loaded_cube.name()}
    redmine_output = RedmineOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'dynamic map', 'map_type': 'invalid'})
    iris.save(cube, init['src'][0])
    result = redmine_output.presentation_object(init['src'][0], init['local_dst'])
    assert result is None

    cube = iris.cube.Cube([0], attributes={'type': 'dynamic map', 'map_type': 'global ocean'})
    iris.save(cube, init['src'][0])
    monkeypatch.setattr("helpers.presentation_objects.make_dynamic_map.__code__", mockreturn.__code__)
    result = redmine_output.presentation_object(init['src'][0], init['local_dst'])
    assert result == {'presentation_type': 'image', **mockreturn(init['src'][0], init['local_dst'], cube)}

def test_presentation_object_invalid_diagnostic_type(tmpdir, monkeypatch):
    init = {
        "src": [str(tmpdir) + "/test.nc"],
        "local_dst": "",
        "template": "./template.txt.j2",
        "subject": "Test Issue",
        "api_key": "Invalid Key"
    }
    redmine_output = RedmineOutput(init)

    cube = iris.cube.Cube([0], attributes={'type': 'invalid'})
    iris.save(cube, init['src'][0])
    with patch.object(redmine_output, 'log_warning') as mock:
        assert redmine_output.presentation_object(init['src'][0], init['local_dst']) is None
    mock.assert_called_with(f"Invalid diagnostic type {cube.attributes['type']}")