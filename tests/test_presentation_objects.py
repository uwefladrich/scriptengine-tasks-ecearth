"""Tests for helpers/presentation_objects.py"""

import datetime

import pytest
import cf_units
import iris
import matplotlib.pyplot as plt

import helpers.presentation_objects as po
import helpers.exceptions as exceptions

def test_format_title():
    assert po.format_title("test_title") == "Test Title"
    test_unit = cf_units.Unit("1")
    assert po.format_title("test_title", units=test_unit) == "Test Title"
    test_unit = cf_units.Unit("kilometers")
    assert po.format_title("test_title", units=test_unit) == "Test Title / 1000 m"

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

def test_make_map(tmpdir, monkeypatch):
    path = './tests/testdata/tos-climatology.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    def mockreturn(*args, **kwargs):
        return plt.figure()
    
    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = po.make_map(path, dst_folder, cube)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos-climatology.png',
        'comment': cube.attributes['comment'],
    }
    assert result == expected_result

def test_make_time_map(tmpdir, monkeypatch):
    path = './tests/testdata/tos-annual-map.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    def mockreturn(*args, **kwargs):
        return plt.figure()
    
    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = po.make_time_map(path, dst_folder, cube)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos-annual-map.gif',
        'comment': cube.attributes['comment'],
    }
    assert result == expected_result

def test_make_time_map_map_handling_exception(tmpdir):
    path = './tests/testdata/tos-annual-map.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    cube.attributes['map_type'] = 'invalid type'
    with pytest.raises(exceptions.InvalidMapTypeException):
        po.make_time_map(path, dst_folder, cube)

def test_make_map_map_handling_exception(tmpdir):
    path = './tests/testdata/tos-climatology.nc'
    dst_folder = str(tmpdir)
    cube = iris.load_cube(path)
    cube.attributes['map_type'] = 'invalid type'
    with pytest.raises(exceptions.InvalidMapTypeException):
        po.make_map(path, dst_folder, cube)

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
