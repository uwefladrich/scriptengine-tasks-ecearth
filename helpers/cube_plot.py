"""Helper module to plot Iris monitoring cubes."""

import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cftime
import math

def _title(name, units=None):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ").title()
    if not (
        units == None 
        or units.is_unknown() 
        or units.is_no_unit()
        ):
        if qplt._use_symbol(units):
            units = units.symbol
        title += " / {}".format(units)
    return title

def ts_plot(ts_cube):
    """
    Plot a monitoring time series cube.
    """
    time_coord = ts_cube.dim_coords[0]
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
    
    plt.tight_layout()
    plt.title(_title(ts_cube.long_name))
    plt.xlabel(_title(time_coord.name()))
    plt.ylabel(_title(ts_cube.name(), ts_cube.units))
