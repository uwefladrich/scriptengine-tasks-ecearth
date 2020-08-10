"""Tests for helpers/cube_plot.py"""

import datetime

import pytest
import cf_units

import helpers.cube_plot as cube_plot

def test_format_title():
    assert "Test Title" == cube_plot.format_title("test_title")
    unit = cf_units.Unit("1")
    assert "Test Title" == cube_plot.format_title("test_title", units=unit)
    unit = cf_units.Unit("kilometers")
    assert "Test Title / 1000 m" == cube_plot.format_title("test_title", units=unit)

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
    assert expected_result == cube_plot.format_units(unit)


def test_format_dates():
    current_date = datetime.datetime.now()
    changed_year = datetime.datetime(current_date.year - 1, current_date.month, current_date.day)
    changed_month = datetime.datetime(current_date.year, (current_date.month + 1) % 12, current_date.day)
    assert [current_date.year, changed_year.year] == cube_plot.format_dates([current_date, changed_year])
    assert [current_date.strftime("%Y-%m"), changed_month.strftime("%Y-%m")] == cube_plot.format_dates([current_date, changed_month])