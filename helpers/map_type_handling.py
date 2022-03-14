"""Module containing plot functions for different map types."""

import warnings

import cartopy.crs as ccrs
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt


def function_mapper(map_type_string):
    mapper = {
        "global ocean": global_ocean_plot,
        "global atmosphere": global_atmosphere_plot,
        "polar ice sheet": polar_ice_sheet_plot,
    }
    return mapper.get(map_type_string, None)


def global_ocean_plot(
    cube,
    title=None,
    dates=None,
    units=None,
    value_range=[None, None],
    colormap="RdBu_r",
    **kwargs
):
    """Map Type Handling for Global Ocean Maps"""
    fig = plt.figure(figsize=(6, 4), dpi=150)
    fig.suptitle(title)
    ax = fig.add_subplot(
        1,
        1,
        1,
        projection=ccrs.PlateCarree(),
        facecolor="#d3d3d3",
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            action="ignore",
            message="Coordinate system of latitude and longitude ",
            category=UserWarning,
        )
        warnings.filterwarnings(
            action="ignore",
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
            vmin=value_range[0],
            vmax=value_range[1],
            cmap=colormap,
        )
    cbar = fig.colorbar(im, orientation="horizontal")
    cbar.set_label(units)
    ax.set_title(dates, fontdict={"fontsize": 8, "fontweight": "medium"})
    ax.coastlines()
    return fig


def global_atmosphere_plot(
    cube,
    title=None,
    dates=None,
    units=None,
    value_range=[None, None],
    colormap="RdBu_r",
    **kwargs
):
    """Map Type Handling for Global Atmosphere Maps"""
    fig = plt.figure(figsize=(6, 4), dpi=150)
    fig.suptitle(title)
    ax = fig.add_subplot(
        1,
        1,
        1,
        projection=ccrs.PlateCarree(),
        facecolor="#d3d3d3",
    )
    longitude = cube.coord("longitude").points
    latitude = cube.coord("latitude").points
    data = cube.data
    im = plt.scatter(
        longitude,
        latitude,
        s=1,
        c=data,
        axes=ax,
        vmin=value_range[0],
        vmax=value_range[1],
        cmap=colormap,
        transform=ccrs.PlateCarree(),
    )
    cbar = fig.colorbar(im, orientation="horizontal")
    cbar.set_label(units)
    ax.set_title(dates, fontdict={"fontsize": 8, "fontweight": "medium"})
    ax.coastlines()
    return fig


def polar_ice_sheet_plot(
    cube,
    title=None,
    dates=None,
    units=None,
    value_range=[None, None],
    colormap="RdBu_r",
    **kwargs
):
    fig = plt.figure(figsize=(6, 4), dpi=150)
    fig.suptitle(title)
    if "north" in cube.long_name or "North" in cube.long_name:
        center = 90.0
    else:
        center = -90.0
    ax = fig.add_subplot(
        1,
        1,
        1,
        projection=ccrs.Orthographic(central_latitude=center),
        facecolor="#d3d3d3",
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            action="ignore",
            message="Coordinate system of latitude and longitude ",
            category=UserWarning,
        )
        warnings.filterwarnings(
            action="ignore",
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
            vmin=value_range[0],
            vmax=value_range[1],
            cmap=colormap,
        )
    bar = fig.colorbar(im, orientation="horizontal")
    if units:
        bar.set_label(units)
    ax.set_title(dates, fontdict={"fontsize": 8, "fontweight": "medium"})
    ax.coastlines()
    return fig
