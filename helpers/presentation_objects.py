"""
Initialize presentation objects for visualization
"""

import os
import math

import cftime
import matplotlib.pyplot as plt
import imageio
import iris.quickplot as qplt

from helpers.file_handling import ChangeDirectory
import helpers.exceptions as exceptions
import helpers.map_type_handling as type_handling

def make_time_series(src_path, dst_folder, time_series_cube):
    """
    Load time series diagnostic and call plot creator.
    """
    # get file name without extension
    base_name = os.path.splitext(os.path.basename(src_path))[0]
    dst_file = f"./{base_name}.png"

    x_coord = time_series_cube.coords()[0]
    if "second since" in x_coord.units.name:
        dates = cftime.num2pydate(x_coord.points, x_coord.units.name)
        coord_points = format_dates(dates)
    else:
        coord_points = x_coord.points
    
    fig = plt.figure(figsize=(6, 4), dpi=150)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(coord_points, time_series_cube.data, marker='o')
    if "second since" in x_coord.units.name:
        fig.autofmt_xdate()
    minor_step = math.ceil(len(coord_points) / 40)
    if len(coord_points) < 10:
        major_step = minor_step
    elif len(coord_points) < 20:
        major_step = 2*minor_step
    else:
        major_step = 3*minor_step
    ax.set_xticks(coord_points[::major_step])
    ax.set_xticks(coord_points[::minor_step], minor=True)
    ax.set_xticklabels(coord_points[::major_step])
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 6), useOffset=False, useMathText=True)
    ax.set_title(format_title(time_series_cube.long_name))
    ax.set_xlabel(format_title(x_coord.name()))
    ax.set_ylabel(format_title(time_series_cube.long_name, time_series_cube.units))
    plt.tight_layout()
    with ChangeDirectory(dst_folder):
        fig.savefig(dst_file, bbox_inches="tight")
        plt.close(fig)

    image_dict = {
        'title': time_series_cube.attributes['title'],
        'path': dst_file,
        'comment': time_series_cube.attributes['comment'],
    }
    return image_dict

def make_static_map(src_path, dst_folder, static_map_cube):
    """
    Load map diagnostic and determine map type.
    """
    # get file name without extension
    base_name = os.path.splitext(os.path.basename(src_path))[0]
    map_type = static_map_cube.attributes['map_type']
    map_handler = type_handling.function_mapper(map_type)
    if map_handler is None:
        raise exceptions.InvalidMapTypeException(map_type)
    
    unit_text = f"{format_units(static_map_cube.units)}"
    time_coord = static_map_cube.coord('time')
    time_bounds = time_coord.bounds[0]
    dates = cftime.num2pydate(time_bounds, time_coord.units.name)
    plot_title = format_title(static_map_cube.long_name)
    date_title = f"{dates[0].strftime('%Y')} - {dates[-1].strftime('%Y')}"
    fig = map_handler(
        static_map_cube,
        title=plot_title,
        dates=date_title,
        units=unit_text,
    )
    dst_file = f"./{base_name}.png"
    with ChangeDirectory(dst_folder):
        fig.savefig(dst_file, bbox_inches="tight")
        plt.close(fig)

    image_dict = {
        'title': static_map_cube.attributes['title'],
        'path': dst_file,
        'comment': static_map_cube.attributes['comment'],
    }
    return image_dict
    
def make_dynamic_map(src_path, dst_folder, dyn_map_cube):
    """
    Load map diagnostic and determine map type.
    """
    # get file name without extension
    base_name = os.path.splitext(os.path.basename(src_path))[0]
    map_type = dyn_map_cube.attributes['map_type']
    map_handler = type_handling.function_mapper(map_type)
    if map_handler is None:
        raise exceptions.InvalidMapTypeException(map_type)
    
    png_dir = f"{base_name}_frames"
    number_of_time_steps = len(dyn_map_cube.coord('time').points)
    with ChangeDirectory(dst_folder):
        if not os.path.isdir(png_dir):
            os.mkdir(png_dir)
        number_of_pngs = len(os.listdir(png_dir))
    
    value_range = [
        dyn_map_cube.attributes["presentation_min"],
        dyn_map_cube.attributes["presentation_max"]
    ]
    unit_text = f"{format_units(dyn_map_cube.units)}"
    dst_file = f"./{base_name}.gif"
    with ChangeDirectory(f"{dst_folder}/{png_dir}"):
        for time_step in range(number_of_pngs, number_of_time_steps):
            time_coord = dyn_map_cube.coord('time')
            time_bounds = time_coord.bounds[time_step]
            dates = cftime.num2pydate(time_bounds, time_coord.units.name)
            date_title = f"{dates[0].strftime('%Y')}"
            plot_title = format_title(dyn_map_cube.long_name)
            fig = map_handler(
                dyn_map_cube[time_step],
                title=plot_title,
                dates=date_title,
                min_value=value_range[0],
                max_value=value_range[1],
                units=unit_text,
            )
            fig.savefig(f"./{base_name}-{time_step:03}.png", bbox_inches="tight")
            plt.close(fig)   
        images = []
        for file_name in sorted(os.listdir(".")):
            images.append(imageio.imread(file_name))
        imageio.mimsave(f'.{dst_file}', images, fps=2)

    image_dict = {
        'title': dyn_map_cube.attributes['title'],
        'path': dst_file,
        'comment': dyn_map_cube.attributes['comment'],
    }
    return image_dict


def format_title(name, units=None):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ").title()
    unit_text = format_units(units)
    if unit_text and unit_text != "1":
        title += " / {}".format(unit_text)
    return title

def format_units(units):
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

def format_dates(dates):
    fmt_dates = []
    for date in dates:
        fmt_dates.append(date.year)
    if len(set(fmt_dates)) != len(fmt_dates):
        fmt_dates = []
        for date in dates:
            fmt_dates.append(date.strftime("%Y-%m"))
    return fmt_dates
