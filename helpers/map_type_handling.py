"""Module containing plot functions for different map types."""

import warnings

import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
import matplotlib.cm as mpl_cm
import cftime
import cf_units as unit
import cartopy.crs as ccrs

def function_mapper(map_type_string):
    mapper = {
        'global ocean': global_ocean_plot,
        'global atmosphere': global_atmosphere_plot,
        'polar ice sheet': polar_ice_sheet_plot,
    }
    return mapper.get(map_type_string, None)

def global_ocean_plot(cube, title=None, dates=None, units=None, min_value=None, max_value=None):
    """Map Type Handling for Global Ocean Maps"""
    fig = plt.figure(figsize=(6, 4), dpi=300)
    fig.suptitle(title)
    ax = fig.add_subplot(
        1, 1, 1,
        projection=ccrs.PlateCarree(),
        facecolor='#d3d3d3',
        )
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
            cmap='RdBu_r',
            )
    cbar = fig.colorbar(im, orientation='horizontal')
    cbar.set_label(units)
    ax.set_title(dates, fontdict={'fontsize': 8, 'fontweight': 'medium'})
    ax.coastlines()
    return fig

def global_atmosphere_plot(cube, title=None, dates=None, min_value=None, max_value=None, units=None):
    """Map Type Handling for Global Atmosphere Maps"""
    fig = plt.figure(figsize=(6, 4), dpi=300)
    fig.suptitle(title)
    ax = fig.add_subplot(
        1, 1, 1,
        projection=ccrs.PlateCarree(),
        facecolor='#d3d3d3',
        )
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
        cmap='RdBu_r',
    )
    cbar = fig.colorbar(im, orientation='horizontal')
    cbar.set_label(units)
    ax.set_title(dates, fontdict={'fontsize': 8, 'fontweight': 'medium'})
    ax.coastlines()
    return fig

def polar_ice_sheet_plot(cube, title=None, dates=None, min_value=None, max_value=None, units=None):
    fig = plt.figure(figsize=(6,4), dpi=300)
    fig.suptitle(title)
    if cube.var_name.endswith('n'):
        center = 90.0
    else:
        center = -90.0
    ax = fig.add_subplot(
        1, 1, 1,
        projection=ccrs.Orthographic(central_latitude=center),
        facecolor='#d3d3d3',
        )
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
            cmap='RdBu_r',
            )
    bar = fig.colorbar(im, orientation='horizontal')
    if units:
        bar.set_label(units)
    ax.set_title(dates, fontdict={'fontsize': 8, 'fontweight': 'medium'})
    ax.coastlines()
    return fig
