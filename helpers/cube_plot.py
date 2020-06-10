"""Helper module to plot Iris monitoring cubes."""

import os
import imageio

import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cftime
import cf_units as unit
import math
import numpy as np

from helpers.file_handling import cd
import helpers.map_type_handling as type_handling
from helpers.exceptions import InvalidMapTypeException

def _title(name, units=None):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ").title()
    unit_text = fmt_units(units)
    if unit_text:
        title += " / {}".format(unit_text)
    return title

def fmt_units(units):
    if not (
        units == None 
        or units.is_unknown() 
        or units.is_no_unit()
    ):
        if qplt._use_symbol(units):
            return units.symbol
        else:
            return units
    else:
        return None


def time_series_plot(ts_cube, dst_folder, dst_file):
    """
    Plot a monitoring time series cube.
    """
    time_coord = ts_cube.coord('time')
    dates = cftime.num2pydate(time_coord.points, "seconds since 1900-01-01 00:00")

    fmt_dates = []
    for date in dates:
        fmt_dates.append(date.year)
    if len(set(fmt_dates)) != len(fmt_dates):
        fmt_dates = []
        for date in dates:
            fmt_dates.append(date.strftime("%Y-%m"))

    fig, ax = plt.subplots()
    ax.plot(fmt_dates, ts_cube.data, marker='o')
    fig.autofmt_xdate()    
    minor_step = math.ceil(len(fmt_dates) / 40)
    if len(fmt_dates) < 10:
        major_step = minor_step
    elif len(fmt_dates) < 20:
        major_step = 2*minor_step
    else:
        major_step = 3*minor_step
    ax.set_xticks(fmt_dates[::major_step])
    ax.set_xticks(fmt_dates[::minor_step], minor=True)
    ax.set_xticklabels(fmt_dates[::major_step])
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-3,6), useOffset=False, useMathText=True)
    plt.tight_layout()
    plt.title(_title(ts_cube.long_name))
    plt.xlabel(_title(time_coord.name()))
    plt.ylabel(_title(ts_cube.name(), ts_cube.units))
    with cd(dst_folder):
        plt.savefig(dst_file, bbox_inches="tight")
        plt.close()

def static_map_plot(map_cube, report_folder, base_name):
    """
    Plot a monitoring map cube as a static image.
    """
    map_type = map_cube.attributes['map_type']
    map_handler = type_handling.function_mapper(map_type)
    if not map_handler:
        raise InvalidMapTypeException(map_type)
    axis_labels = [
        "Longitude",
        "Latitude"
    ]
    unit_text = f"{fmt_units(map_cube.units)}"
    map_handler(
        map_cube[0],
        title=_title(map_cube.long_name),
        axis_labels=axis_labels,
        units=unit_text,
    )
    dst = f"./{base_name}.png"
    with cd(report_folder):
        plt.savefig(dst, bbox_inches="tight")
        plt.close()
    
    return dst

def dynamic_map_plot(map_cube, report_folder, base_name):
    """
    Plot a monitoring map cube as an animated GIF.
    """
    png_dir = f"{base_name}_frames"
    number_of_time_steps = len(map_cube.coord('time').points)
    with cd(report_folder):
        if not os.path.isdir(png_dir):
            os.mkdir(png_dir)
        number_of_pngs = len([name for name in os.listdir(png_dir)])
    if number_of_pngs == number_of_time_steps:
        return
    
    value_range = [
        np.ma.min(map_cube.data),
        np.ma.max(map_cube.data),
    ]
    map_type = map_cube.attributes['map_type']
    map_handler = type_handling.function_mapper(map_type)
    if not map_handler:
        raise InvalidMapTypeException(map_type)
    unit_text = f"{fmt_units(map_cube.units)}"

    dst = f"./{base_name}.gif"
    with cd(f"{report_folder}/{png_dir}"):
        for time_step in range(0, number_of_time_steps):
            map_handler(
                map_cube[time_step],
                title=_title(map_cube.long_name),
                value_range=value_range,
                units=unit_text,
            )
            plt.savefig(f"./{base_name}-{time_step}.png", bbox_inches="tight")
            plt.close()   
        images = []
        for file_name in os.listdir("."):
            images.append(imageio.imread(file_name))
        imageio.mimsave(f'.{dst}', images)
    return dst
