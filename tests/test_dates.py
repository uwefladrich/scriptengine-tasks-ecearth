"""Tests for dates helpers"""

import pytest

import helpers.dates


def test_month_number():
    assert helpers.dates.month_number(3) == 3
    assert helpers.dates.month_number("March") == 3
    assert helpers.dates.month_number("march") == 3
    assert helpers.dates.month_number("mar") == 3
    pytest.raises(ValueError, helpers.dates.month_number, "m")
    pytest.raises(ValueError, helpers.dates.month_number, 13)
    pytest.raises(ValueError, helpers.dates.month_number, 0)


def test_month_name():
    assert helpers.dates.month_name(3) == "March"
    assert helpers.dates.month_name("March") == "March"
    assert helpers.dates.month_name("march") == "March"
    assert helpers.dates.month_name("mar") == "March"
