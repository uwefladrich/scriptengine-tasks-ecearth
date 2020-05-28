"""Helper module to plot Iris monitoring cubes."""

import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cftime

def _title(cube_or_coord, with_units):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """

    if isinstance(cube_or_coord, int) or cube_or_coord == None:
        title = ""
    else:
        title = cube_or_coord.name().replace("_", " ").title()
        units = cube_or_coord.units
        if with_units and not (
                units.is_unknown() or units.is_no_unit()
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

    plt.plot(fmt_dates, ts_cube.data, marker='o')
    plt.xticks(fmt_dates, rotation=45)
    plt.tight_layout()
    plt.xlabel(_title(time_coord, False))
    plt.title(_title(ts_cube, False))
    plt.ylabel(_title(ts_cube, True))
