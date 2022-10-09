"""Tests for helpers/presentation_objects.py"""

import datetime
from pathlib import Path

import cf_units
import iris
import matplotlib.pyplot as plt
import pytest
import yaml

from helpers.exceptions import InvalidMapTypeException, PresentationException
from helpers.presentation_objects import (
    MapLoader,
    PresentationObject,
    PresentationObjectLoader,
    ScalarLoader,
    TemporalmapLoader,
    TimeseriesLoader,
    format_dates,
    format_label,
    format_title,
    format_units,
    get_loader,
)


def test_presentation_object():
    abstract_loader = PresentationObjectLoader("")
    pytest.raises(
        NotImplementedError,
        abstract_loader.load,
    )


def test_format_title():
    assert format_title("test_title") == "test title"


def test_format_label():
    assert format_label("test_title") == "test title"
    test_unit = cf_units.Unit("1")
    assert format_label("test_title", units=test_unit) == "test title"
    test_unit = cf_units.Unit("kilometers")
    assert format_label("test_title", units=test_unit) == "test title / 1000 m"


unit = [
    None,
    cf_units.Unit("1"),
    cf_units.Unit("kilometers"),
    cf_units.Unit("degC"),
    cf_units.Unit("no_unit"),
]
expected_result = [None, "1", "1000 m", "degC", None]


@pytest.mark.parametrize("unit, expected_result", zip(unit, expected_result))
def test_format_units(unit, expected_result):
    assert expected_result == format_units(unit)


def test_format_dates():
    current_date = datetime.datetime(1990, 8, 19)
    changed_year = datetime.datetime(1991, 8, 19)
    changed_month = datetime.datetime(1990, 8, 19)
    assert [current_date.year, changed_year.year] == format_dates(
        [current_date, changed_year]
    )
    assert [
        current_date.strftime("%Y-%m"),
        changed_month.strftime("%Y-%m"),
    ] == format_dates([current_date, changed_month])


def test_get_loader_extension():
    test_data = {
        "test.nc": "File not found: test.nc",
        "test.txt": "Invalid file extension: test.txt",
    }
    for src, msg in test_data.items():
        with pytest.raises(PresentationException, match=msg):
            get_loader(Path(src))


def test_get_loader_invalid_diagnostic_type(tmp_path):
    src = tmp_path / "test.nc"
    cube = iris.cube.Cube([0], attributes={"diagnostic_type": "invalid"})
    # Iris before 3.3 can't handle pathlib's Path, needs string
    iris.save(cube, str(src))
    msg = f"Invalid diagnostic type: {cube.attributes['diagnostic_type']}"
    with pytest.raises(PresentationException, match=msg):
        get_loader(src)


def test_map_object(tmp_path, monkeypatch):
    path = "./tests/testdata/tos_nemo_all_mean_map.nc"

    def mockreturn(*args, **kwargs):
        return plt.figure()

    map = PresentationObject(tmp_path, path)
    assert isinstance(map.loader, MapLoader)

    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = map.create_dict()
    cube = iris.load_cube(path)
    expected_result = {
        "title": cube.attributes["title"],
        "path": "./tos_nemo_all_mean_map.png",
        "comment": cube.attributes["comment"],
        "presentation_type": "image",
    }
    assert result == expected_result


def test_temporalmap_object(tmp_path, monkeypatch):
    path = "./tests/testdata/tos_nemo_year_mean_temporalmap.nc"

    def mockreturn(*args, **kwargs):
        return plt.figure()

    temporalmap = PresentationObject(tmp_path, path)
    assert isinstance(temporalmap.loader, TemporalmapLoader)

    monkeypatch.setattr("helpers.map_type_handling.global_ocean_plot", mockreturn)
    result = temporalmap.create_dict()
    cube = iris.load_cube(path)
    expected_result = {
        "title": cube.attributes["title"],
        "path": "./tos_nemo_year_mean_temporalmap.gif",
        "comment": cube.attributes["comment"],
        "presentation_type": "image",
    }
    assert result == expected_result


def test_temporalmap_map_handling_exception(tmp_path):
    path = tmp_path / "test.nc"
    cube = iris.load_cube("./tests/testdata/tos_nemo_year_mean_temporalmap.nc")
    cube.attributes["map_type"] = "invalid type"
    # Iris before 3.3 can't handle pathlib's Path, needs string
    iris.save(cube, str(path))
    temporalmap_object = PresentationObject(tmp_path, path)
    with pytest.raises(InvalidMapTypeException):
        temporalmap_object.create_dict()


def test_map_map_handling_exception(tmp_path):
    path = tmp_path / "test.nc"
    cube = iris.load_cube("./tests/testdata/tos_nemo_all_mean_map.nc")
    cube.attributes["map_type"] = "invalid type"
    iris.save(cube, path)
    map_object = PresentationObject(tmp_path, path)
    with pytest.raises(InvalidMapTypeException):
        map_object.create_dict()


def test_timeseries_object(tmp_path):
    path = "tests/testdata/tos_nemo_global_mean_year_mean_timeseries.nc"
    cube = iris.load_cube(path)
    timeseries_object = PresentationObject(tmp_path, path)
    assert isinstance(timeseries_object.loader, TimeseriesLoader)
    result = timeseries_object.create_dict()
    expected_result = {
        "title": cube.attributes["title"],
        "path": "./" + Path(path).with_suffix(".png").name,
        "comment": cube.attributes["comment"],
        "presentation_type": "image",
    }
    assert result == expected_result


def test_scalar_object_not_found():
    for sdiag_file in ("test.yml", "test.yaml"):
        with pytest.raises(
            PresentationException, match=f"File not found: {sdiag_file}"
        ):
            ScalarLoader(sdiag_file).load()


def test_scalar_object_created(tmp_path):
    sdiag_file = tmp_path / "test.yml"
    sdiag = {"foo": "bar", "eggs": "ham"}
    with open(sdiag_file, "w") as file:
        yaml.dump(sdiag, file)
    sdiag_presentation = PresentationObject("", sdiag_file)
    assert isinstance(sdiag_presentation.loader, ScalarLoader)
    assert sdiag_presentation.create_dict() == {"presentation_type": "text", **sdiag}
