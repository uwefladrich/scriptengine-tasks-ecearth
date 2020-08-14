"""Tests for helpers/presentation_objects.py"""

import datetime
from unittest.mock import patch, Mock

import pytest
import cf_units
import iris
import matplotlib.pyplot as plt

import helpers.presentation_objects as po
import helpers.exceptions as exceptions

def test_format_title():
    assert "Test Title" == po.format_title("test_title")
    unit = cf_units.Unit("1")
    assert "Test Title" == po.format_title("test_title", units=unit)
    unit = cf_units.Unit("kilometers")
    assert "Test Title / 1000 m" == po.format_title("test_title", units=unit)

unit = [
    None,
    cf_units.Unit("1"),
    cf_units.Unit("kilometers"),
    cf_units.Unit("degC"),
    cf_units.Unit("no_unit")
]
expected_result = [
    None,
    "1",
    "1000 m",
    "degC",
    None
]

@pytest.mark.parametrize("unit, expected_result", zip(unit, expected_result))
def test_format_units(unit, expected_result):
    assert expected_result == po.format_units(unit)


def test_format_dates():
    current_date = datetime.datetime.now()
    changed_year = datetime.datetime(current_date.year - 1, current_date.month, current_date.day)
    changed_month = datetime.datetime(current_date.year, (current_date.month + 1) % 12, current_date.day)
    assert [current_date.year, changed_year.year] == po.format_dates([current_date, changed_year])
    assert [current_date.strftime("%Y-%m"), changed_month.strftime("%Y-%m")] == po.format_dates([current_date, changed_month])

def test_make_static_map(tmpdir, monkeypatch):
    path = './tests/testdata/tos-climatology.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    def mockreturn(*args, **kwargs):
        return plt.figure()
    
    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = po.make_static_map(path, dst_folder, cube)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos-climatology.png',
        'comment': cube.attributes['comment'],
    }
    assert result == expected_result

def test_make_dynamic_map(tmpdir, monkeypatch):
    path = './tests/testdata/tos-annual-map.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    def mockreturn(*args, **kwargs):
        return plt.figure()
    
    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = po.make_dynamic_map(path, dst_folder, cube)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos-annual-map.gif',
        'comment': cube.attributes['comment'],
    }
    assert result == expected_result

def test_make_dynamic_map_map_handling_exception(tmpdir, monkeypatch):
    path = './tests/testdata/tos-annual-map.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    cube.attributes['map_type'] = 'invalid type'
    with pytest.raises(exceptions.InvalidMapTypeException):
        result = po.make_dynamic_map(path, dst_folder, cube)

def test_make_static_map_map_handling_exception(tmpdir, monkeypatch):
    path = './tests/testdata/tos-climatology.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    cube.attributes['map_type'] = 'invalid type'
    with pytest.raises(exceptions.InvalidMapTypeException):
        result = po.make_static_map(path, dst_folder, cube)

def test_make_time_series(tmpdir):
    path = './tests/testdata/tos-global-avg.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)

    result = po.make_time_series(path, dst_folder, cube)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos-global-avg.png',
        'comment': cube.attributes['comment'],
    }
    assert result == expected_result
