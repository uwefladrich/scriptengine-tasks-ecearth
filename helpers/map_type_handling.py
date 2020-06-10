"""Module containing plot functions for different map types."""

import iris
import iris.quickplot as qplt
import iris.plot as iplt
import matplotlib.pyplot as plt
import cftime
import cf_units as unit
import math
import cartopy.crs as ccrs

def function_mapper(map_type_string):
    mapper = {
        'global ocean': global_ocean_plot,
    }
    return mapper.get(map_type_string, None)

def global_ocean_plot(cube, title=None, value_range=None, units=None):
    plt.figure(dpi=300)
    ax = plt.subplot(projection=ccrs.PlateCarree())
    projected_cube, _ = iris.analysis.cartography.project(
        cube, 
        ccrs.PlateCarree(),
        nx=800,
        ny=400,
        )
    im = iplt.pcolormesh(
        projected_cube,
        axes=ax,
        clim=value_range
        )
    bar = plt.colorbar(im, orientation='horizontal')
    bar.set_label(units)
    ax.set_title(title)
    ax.coastlines()

    