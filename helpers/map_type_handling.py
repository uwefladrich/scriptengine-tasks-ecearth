"""Module containing plot functions for different map types."""

import warnings

import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
import cftime
import cf_units as unit
import cartopy.crs as ccrs

import helpers.exceptions as exceptions

def function_mapper(map_type_string):
    mapper = {
        'global ocean': global_ocean_plot,
        'global atmosphere': global_atmosphere_plot,
        'polar ice sheet': polar_ice_sheet_plot,
    }
    try:
        return mapper[map_type_string]
    except KeyError:
        raise exceptions.InvalidMapTypeException(map_type_string)

def global_ocean_plot(cube, title=None, units=None, min_value=None, max_value=None):
    """Map Type Handling for Global Ocean Maps"""
    fig = plt.figure(figsize=(6, 4), dpi=300)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    with warnings.catch_warnings():
        warnings.filterwarnings(
            action='ignore',
            message="Coordinate system of latitude and longitude ",
            category=UserWarning,
            )
        warnings.filterwarnings(
            action='ignore',
            message="Coordinate 'projection_._coordinate' is",
            category=UserWarning,
            )
        projected_cube, _ = iris.analysis.cartography.project(
            cube,
            ccrs.PlateCarree(),
            nx=800,
            ny=400,
            )
        im = iplt.pcolormesh(
            projected_cube,
            axes=ax,
            vmin=min_value,
            vmax=max_value,
            )
    cbar = fig.colorbar(im, orientation='horizontal')
    cbar.set_label(units)
    ax.set_title(title)
    ax.coastlines()
    return fig

def global_atmosphere_plot(cube, title=None, min_value=None, max_value=None, units=None):
    """Map Type Handling for Global Atmosphere Maps"""
    fig = plt.figure(figsize=(6, 4), dpi=300)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    longitude = cube.coord('longitude').points
    latitude = cube.coord('latitude').points
    data = cube.data
    im = plt.scatter(
        longitude,
        latitude,
        s=1,
        c=data,
        axes=ax,
        vmin=min_value,
        vmax=max_value,
        transform=ccrs.PlateCarree(),
    )
    cbar = fig.colorbar(im, orientation='horizontal')
    cbar.set_label(units)
    ax.set_title(title)
    ax.coastlines()
    return fig

def polar_ice_sheet_plot(cube, title=None, min_value=None, max_value=None, units=None):
    fig = plt.figure(figsize=(6,4), dpi=300)
    if cube.var_name.endswith('n'):
        center = 90.0
    else:
        center = -90.0
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(central_latitude=center))
    with warnings.catch_warnings():
        warnings.filterwarnings(
            action='ignore', 
            message="Coordinate system of latitude and longitude ", 
            category=UserWarning,
            )
        warnings.filterwarnings(
            action='ignore', 
            message="Coordinate 'projection_._coordinate' is", 
            category=UserWarning,
            )
        projected_cube, _ = iris.analysis.cartography.project(
            cube, 
            ccrs.PlateCarree(),
            nx=800,
            ny=400,
            )
        im = iplt.pcolormesh(
            projected_cube,
            axes=ax,
            vmin=min_value,
            vmax=max_value,
            )
    bar = fig.colorbar(im, orientation='horizontal')
    if units != "1":
        bar.set_label(units)
    time_coord = cube.coord('time')
    date = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
    month = date.strftime("%m")
    ax.set_title(f"{title} ({month})")
    ax.coastlines()
    return fig
