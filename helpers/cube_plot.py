"""Helper module to plot Iris monitoring cubes."""

import os
import imageio

import math
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cftime
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
    """Format Cube Units as String"""
    if not (
            units is None
            or units.is_unknown()
            or units.is_no_unit()
        ):
        if qplt._use_symbol(units):
            return units.symbol
        else:
            return units
    else:
        return None


def plot_time_series(ts_cube, dst_folder, dst_file):
    """
    Plot a monitoring time series cube.
    """
    time_coord = ts_cube.coord('time')
    dates = cftime.num2pydate(time_coord.points, time_coord.units.name)

    fmt_dates = []
    for date in dates:
        fmt_dates.append(date.year)
    if len(set(fmt_dates)) != len(fmt_dates):
        fmt_dates = []
        for date in dates:
            fmt_dates.append(date.strftime("%Y-%m"))

    fig = plt.figure(figsize=(6, 4), dpi=300)
    ax = fig.add_subplot(1, 1, 1)
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
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 6), useOffset=False, useMathText=True)
    ax.set_title(_title(ts_cube.long_name))
    ax.set_xlabel(_title(time_coord.name()))
    ax.set_ylabel(_title(ts_cube.name(), ts_cube.units))
    plt.tight_layout()
    with cd(dst_folder):
        fig.savefig(dst_file, bbox_inches="tight")
        plt.close(fig)

def plot_static_map(map_cube, report_folder, base_name):
    """
    Plot a monitoring map cube as a static image.
    """
    map_type = map_cube.attributes['map_type']
    map_handler = type_handling.function_mapper(map_type)
    if not map_handler:
        raise InvalidMapTypeException(map_type)

    unit_text = f"{fmt_units(map_cube.units)}"
    value_range = [
        np.ma.min(map_cube.data),
        np.ma.max(map_cube.data),
    ]
    time_coord = map_cube.coord('time')
    dates = cftime.num2pydate(time_coord.bounds[0], time_coord.units.name)
    start_year = dates[0].strftime("%Y")
    end_year = dates[-1].strftime("%Y")
    plot_title = f"{_title(map_cube.long_name)} {start_year} - {end_year}"
    fig = map_handler(
        map_cube[0],
        title=plot_title,
        value_range=value_range,
        units=unit_text,
    )
    dst = f"./{base_name}-{map_cube.var_name}.png"
    with cd(report_folder):
        fig.savefig(dst, bbox_inches="tight")
        plt.close(fig)
    return dst

def plot_dynamic_map(map_cube, report_folder, base_name):
    """
    Plot a monitoring map cube as an animated GIF.
    """
    png_dir = f"{base_name}-{map_cube.var_name}_frames"
    number_of_time_steps = len(map_cube.coord('time').points)
    with cd(report_folder):
        if not os.path.isdir(png_dir):
            os.mkdir(png_dir)
        number_of_pngs = len(os.listdir(png_dir))

    mean = np.ma.mean(map_cube[0].data)
    delta = abs(np.ma.max(map_cube[0].data)) - abs(mean)
    value_range = [
        mean - 1.3 * delta,
        mean + 1.3 * delta,
    ]
    map_type = map_cube.attributes['map_type']
    map_handler = type_handling.function_mapper(map_type)
    if not map_handler:
        raise InvalidMapTypeException(map_type)
    unit_text = f"{fmt_units(map_cube.units)}"

    dst = f"./{base_name}-{map_cube.var_name}.gif"
    with cd(f"{report_folder}/{png_dir}"):
        for time_step in range(number_of_pngs, number_of_time_steps):
            time_coord = map_cube[time_step].coord('time')
            date = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
            year = date.strftime("%Y")
            plot_title = f"{_title(map_cube.long_name)} {year}"
            fig = map_handler(
                map_cube[time_step],
                title=plot_title,
                value_range=value_range,
                units=unit_text,
            )
            fig.savefig(f"./{base_name}-{map_cube.var_name}-{time_step:03}.png", bbox_inches="tight")
            plt.close(fig)   
        images = []
        for file_name in sorted(os.listdir(".")):
            images.append(imageio.imread(file_name))
        imageio.mimsave(f'.{dst}', images, fps=2)
    return dst
