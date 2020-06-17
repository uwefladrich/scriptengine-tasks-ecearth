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
