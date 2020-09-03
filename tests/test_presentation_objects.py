"""Tests for helpers/presentation_objects.py"""

import datetime

import pytest
import cf_units
import iris
import matplotlib.pyplot as plt
import yaml

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
    changed_year = datetime.datetime(current_date.year - 1, current_date.month, 25)
    changed_month = datetime.datetime(current_date.year, (current_date.month + 1) % 12, 25)
    assert [current_date.year, changed_year.year] == po.format_dates([current_date, changed_year])
    assert [current_date.strftime("%Y-%m"), changed_month.strftime("%Y-%m")] == po.format_dates([current_date, changed_month])

def test_get_loader_extension():
    src = ["test.nc", "test.txt"]
    error_messages = [
        f"File not found! Ignoring {src[0]}",
        f"Invalid file extension of {src[1]}",
    ]
    
    for src, msg in zip(src, error_messages):
        with pytest.raises(exceptions.PresentationException, match=msg):
            po.get_loader(src)

def test_get_loader_invalid_diagnostic_type(tmpdir):
    src = str(tmpdir) + "/test.nc"
    cube = iris.cube.Cube([0], attributes={'diagnostic_type': 'invalid'})
    iris.save(cube, src)
    msg = f"Invalid diagnostic type {cube.attributes['diagnostic_type']}"
    with pytest.raises(exceptions.PresentationException, match=msg):
            po.get_loader(src)

def test_map_object(tmpdir, monkeypatch):
    path = './tests/testdata/tos_nemo_all_mean_map.nc'
    dst_folder = str(tmpdir)
    def mockreturn(*args, **kwargs):
        return plt.figure()
    
    map_object = po.PresentationObject(dst_folder, path)
    assert isinstance(map_object.loader, po.MapLoader)
    
    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = map_object.create_dict()
    cube = iris.load_cube(path)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos_nemo_all_mean_map.png',
        'comment': cube.attributes['comment'],
        'presentation_type': 'image',
    }
    assert result == expected_result

def test_temporalmap_object(tmpdir, monkeypatch):
    path = './tests/testdata/tos_nemo_year_mean_temporalmap.nc'
    dst_folder = str(tmpdir)
    def mockreturn(*args, **kwargs):
        return plt.figure()
    
    temporalmap_object = po.PresentationObject(dst_folder, path)
    assert isinstance(temporalmap_object.loader, po.TemporalmapLoader)
    
    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = temporalmap_object.create_dict()
    cube = iris.load_cube(path)
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos_nemo_year_mean_temporalmap.gif',
        'comment': cube.attributes['comment'],
        'presentation_type': 'image',
    }
    assert result == expected_result

def test_temporalmap_map_handling_exception(tmpdir):
    dst_folder = str(tmpdir)
    path = str(tmpdir) + 'test.nc'
    cube = iris.load_cube('./tests/testdata/tos_nemo_year_mean_temporalmap.nc')
    cube.attributes['map_type'] = 'invalid type'
    iris.save(cube, path)
    temporalmap_object = po.PresentationObject(dst_folder, path)
    with pytest.raises(exceptions.InvalidMapTypeException):
        temporalmap_object.create_dict()

def test_map_map_handling_exception(tmpdir):
    dst_folder = str(tmpdir)
    path = str(tmpdir) + 'test.nc'
    cube = iris.load_cube('./tests/testdata/tos_nemo_all_mean_map.nc')
    cube.attributes['map_type'] = 'invalid type'
    iris.save(cube, path)
    map_object = po.PresentationObject(dst_folder, path)
    with pytest.raises(exceptions.InvalidMapTypeException):
        map_object.create_dict()

def test_timeseries_object(tmpdir):
    dst_folder = str(tmpdir)
    path = './tests/testdata/tos_nemo_global_mean_year_mean_timeseries.nc'
    cube = iris.load_cube(path)
    timeseries_object = po.PresentationObject(dst_folder, path)
    assert isinstance(timeseries_object.loader, po.TimeseriesLoader)
    result = timeseries_object.create_dict()
    expected_result = {
        'title': cube.attributes['title'],
        'path': './tos_nemo_global_mean_year_mean_timeseries.png',
        'comment': cube.attributes['comment'],
        'presentation_type': 'image',
    }
    assert result == expected_result

def test_scalar_object(tmpdir):
    src = ["test.yml", "test.yaml"]
    error_messages = [
        f"File not found! Ignoring {src[0]}",
        f"File not found! Ignoring {src[1]}",
    ]
    for src, msg in zip(src, error_messages):
        with pytest.raises(exceptions.PresentationException, match=msg):
            po.ScalarLoader(src).load()

    src = str(tmpdir) + "/test.yml"
    dct = {"foo": "bar", "eggs": "ham"}
    with open(src, 'w') as file:
        yaml.dump(dct, file)
    scalar_object = po.PresentationObject("", src)
    assert isinstance(scalar_object.loader, po.ScalarLoader)
    result = scalar_object.create_dict()
    assert result == {'presentation_type': 'text', **dct}