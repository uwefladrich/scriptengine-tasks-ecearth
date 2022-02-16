"""Tests for helpers/map_type_handling.py"""

import iris
import matplotlib.pyplot as plt

import helpers.map_type_handling as mth


def test_global_ocean_plot():
    ocean_cube = iris.load_cube("./tests/testdata/tos_nemo_all_mean_map.nc")
    assert isinstance(mth.global_ocean_plot(ocean_cube), plt.Figure)


def test_ice_sheet_plot():
    ice_cube = iris.load_cube("./tests/testdata/sithic-north-mar.nc")
    assert isinstance(mth.polar_ice_sheet_plot(ice_cube), plt.Figure)


def test_global_atmosphere_plot():
    atmo_cube = iris.load_cube("./tests/testdata/tas-climatology.nc")
    assert isinstance(mth.global_atmosphere_plot(atmo_cube), plt.Figure)


def test_function_mapper():
    assert mth.function_mapper("global ocean") == mth.global_ocean_plot
    assert mth.function_mapper("global atmosphere") == mth.global_atmosphere_plot
    assert mth.function_mapper("polar ice sheet") == mth.polar_ice_sheet_plot
    assert mth.function_mapper("invalid") is None
