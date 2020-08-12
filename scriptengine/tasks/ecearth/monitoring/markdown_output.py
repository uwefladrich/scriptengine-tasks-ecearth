"""Presentation Task that saves Data and Plots to a Markdown File."""

import os
import math

import jinja2
import yaml
import iris
import cftime
import matplotlib.pyplot as plt
import imageio

from scriptengine.tasks.base import Task
from scriptengine.tasks.base.timing import timed_runner
from scriptengine.jinja import filters as j2filters
from helpers.file_handling import ChangeDirectory
from helpers.cube_plot import format_units, format_title, format_dates
import helpers.exceptions as exceptions
import helpers.map_type_handling as type_handling

class MarkdownOutput(Task):
    """MarkdownOutput Presentation Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
            "template",
        ]
        super().__init__(__name__, parameters, required_parameters=required)

    @timed_runner
    def run(self, context):
        sources = self.getarg('src', context)
        dst_folder = self.getarg('dst', context)
        template = self.getarg('template', context)
        self.log_info(f"Create Markdown report at {dst_folder}.")
        self.log_debug(f"Template: {template}, Source File(s): {sources}")

        presentation_list = []
        for src in sources:
            presentation_list.append(self.presentation_object(src, dst_folder))
        presentation_list = [item for item in presentation_list if item]

        search_path = ['.', 'templates']
        if "_se_cmd_cwd" in context:
            search_path.extend([context["_se_cmd_cwd"],
                                os.path.join(context["_se_cmd_cwd"], "templates")])
        self.log_debug(f"Search path for template: {search_path}")

        loader = jinja2.FileSystemLoader(search_path)
        environment = jinja2.Environment(loader=loader)
        for name, function in j2filters().items():
            environment.filters[name] = function
        md_template = environment.get_template(template)

        with ChangeDirectory(dst_folder):
            with open("./summary.md", 'w') as md_out:
                md_out.write(md_template.render(
                    presentation_list=presentation_list,
                ))
    
    def presentation_object(self, src, dst_folder):
        if src.endswith('.yml'):
            try:
                with open(src) as yml_file:
                    loaded_dict = yaml.load(yml_file, Loader=yaml.FullLoader)
                return {'presentation_type': 'text', **loaded_dict}
            except FileNotFoundError:
                self.log_error(f"File not found! Ignoring {src}")
                return None
        elif src.endswith('.nc'):
            try:
                loaded_cube = iris.load_cube(src)
            except OSError:
                self.log_error(f"File not found! Ignoring {src}")
                return None
            if loaded_cube.attributes["type"] == "time series":
                self.log_debug(f"Loading time series diagnostic {src}")
                return {'presentation_type': 'image', **make_time_series(src, dst_folder, loaded_cube)}
            elif loaded_cube.attributes["type"] == "static map":
                self.log_debug(f"Loading static map diagnostic {src}")
                try:
                    map_plot_dict = make_static_map(src, dst_folder, loaded_cube)
                except exceptions.InvalidMapTypeException as msg:
                    self.log_error(f"Invalid Map Type {msg}")
                    return None
                return {'presentation_type': 'image', **map_plot_dict}
            elif loaded_cube.attributes["type"] == "dynamic map":
                self.log_debug(f"Loading dynamic map diagnostic {src}")
                try:
                    map_plot_dict = make_dynamic_map(src, dst_folder, loaded_cube)
                except exceptions.InvalidMapTypeException as msg:
                    self.log_error(f"Invalid Map Type {msg}")
                    return None
                return {'presentation_type': 'image', **map_plot_dict}
            else:
                self.log_error(f"Invalid diagnostic type {loaded_cube.attributes['type']}")
        else:
            self.log_error(f"Invalid file extension of {src}")
        return None


def make_time_series(src_path, dst_folder, time_series_cube):
    """
    Load time series diagnostic and call plot creator.
    """
    # get file name without extension
    base_name = os.path.splitext(os.path.basename(src_path))[0]
    dst_file = f"./{base_name}.png"

    x_coord = time_series_cube.coords()[0]
    if "seconds since" in x_coord.name():
        dates = cftime.num2pydate(x_coord.points, x_coord.units.name)
        coord_points = format_dates(dates)
    else:
        coord_points = x_coord.points
    
    fig = plt.figure(figsize=(6, 4), dpi=300)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(coord_points, time_series_cube.data, marker='o')
    if "seconds since" in x_coord.name():
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
