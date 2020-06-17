"""Presentation Task that saves Data and Plots to a Markdown File."""

import os

import jinja2
import yaml
import iris
import cftime
import matplotlib.pyplot as plt
import imageio

from scriptengine.tasks.base import Task
from scriptengine.jinja import filters as j2filters
from helpers.file_handling import cd
from helpers.cube_plot import plot_time_series, fmt_units, _title
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

    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        template = self.getarg('template', context)

        scalars = []
        nc_plots = []
        for path in src:
            if path.endswith('.yml'):
                scalars.append(self.load_yaml(path))
            elif path.endswith('.nc'):
                nc_plots.append(self.load_netcdf(path, dst))
            else:
                self.log_warning(f"{path} does not end in .nc or .yml. Ignored.")

        scalars = [scalar for scalar in scalars if scalar]
        nc_plots = [nc_plot for nc_plot in nc_plots if nc_plot]

        exp_id = None
        for scalar in scalars:
            if scalar["long_name"] == "Experiment ID":
                exp_id = scalar["data"]

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

        with cd(dst):
            with open("./summary.md", 'w') as md_out:
                md_out.write(md_template.render(
                    scalar_diagnostics=scalars,
                    nc_diagnostics=nc_plots,
                    exp_id=exp_id,
                ))

    def load_yaml(self, yaml_path):
        try:
            with open(yaml_path) as yml_file:
                loaded_dict = yaml.load(yml_file, Loader=yaml.FullLoader)
            return loaded_dict
        except FileNotFoundError:
            self.log_warning(f"FileNotFoundError: Ignoring {yaml_path}.")
            return None

    def load_netcdf(self, path, dst_folder):
        """
        Load netCDF file and determine diagnostic type.
        """
        try:
            cubes = iris.load(path)
        except IOError:
            self.log_warning(f"IOError, file not found: Ignoring {path}.")
            return None

        if cubes[0].attributes['type'] == 'time series':
            new_plots = self.load_time_series(cubes, path, dst_folder)
        elif cubes[0].attributes['type'] == 'static map':
            new_plots = self.load_static_map(cubes, path, dst_folder)
        elif cubes[0].attributes['type'] == 'dynamic map':
            new_plots = self.load_dynamic_map(cubes, path, dst_folder)

        return new_plots

    def load_time_series(self, cube_list, path, dst_folder):
        """
        Load time series diagnostic and call plot creator.
        """
        self.log_debug(f"Loading time series diagnostic {path}")
        # get file name without extension
        base_name = os.path.splitext(os.path.basename(path))[0]
        plot_list = []
        long_name_list = []
        if len(cube_list) == 1:
            cube = cube_list[0]
            dst_file = f"./{base_name}.png"
            plot_time_series(cube, dst_folder, dst_file)
            self.log_debug(f"New plot created at {dst_folder}.")
            long_name_list.append(cube.long_name)
            plot_list.append(dst_file)
        else:
            for cube in cube_list:
                dst_file = f"./{base_name}-{cube.var_name}.png"
                long_name = cube.long_name
                plot_time_series(cube, dst_folder, dst_file)
                self.log_debug(f"New plot created at {dst_folder}.")
                plot_list.append(dst_file)
                long_name_list.append(long_name)

        new_plots = {
            'plot': plot_list,
            'long_name': long_name_list,
            'title': cube_list[0].metadata.attributes["title"],
            'comment': cube_list[0].metadata.attributes["comment"],
        }
        return new_plots

    def load_static_map(self, static_map_cube, path, dst_folder):
        """
        Load map diagnostic and determine map type.
        """
        static_map_cube = static_map_cube[0]
        self.log_debug(f"Loading static map diagnostic {path}")
        # get file name without extension
        base_name = os.path.splitext(os.path.basename(path))[0]
        map_type = static_map_cube.attributes['map_type']
        try:
            map_handler = type_handling.function_mapper(map_type)
        except exceptions.InvalidMapTypeException as msg:
            self.log_warning(f"Invalid Map Type: {msg}")
            return
        
        unit_text = f"{fmt_units(static_map_cube.units)}"
        time_coord = static_map_cube.coord('time')
        dates = cftime.num2pydate(time_coord.bounds[0], time_coord.units.name)
        start_year = dates[0].strftime("%Y")
        end_year = dates[-1].strftime("%Y")
        plot_title = f"{_title(static_map_cube.long_name)} {start_year} - {end_year}"
        fig = map_handler(
            static_map_cube[0],
            title=plot_title,
            value_range=[None,None],
            units=unit_text,
        )
        dst = f"./{base_name}.png"
        with cd(dst_folder):
            fig.savefig(dst, bbox_inches="tight")
            plt.close(fig)
        new_plot = {
            'plot': [dst],
            'long_name': [static_map_cube.long_name],
            'title': static_map_cube.metadata.attributes["title"],
            'comment': static_map_cube.metadata.attributes["comment"],
        }
        return new_plot
    
    def load_dynamic_map(self, dyn_map_cube, path, dst_folder):
        """
        Load map diagnostic and determine map type.
        """
        dyn_map_cube = dyn_map_cube[0]
        self.log_debug(f"Loading dynamic map diagnostic {path}")
        # get file name without extension
        base_name = os.path.splitext(os.path.basename(path))[0]
        map_type = dyn_map_cube.attributes['map_type']
        try:
            map_handler = type_handling.function_mapper(map_type)
        except exceptions.InvalidMapTypeException as msg:
            self.log_warning(f"Invalid Map Type: {msg}")
            return
        
        png_dir = f"{base_name}-{dyn_map_cube.var_name}_frames"
        number_of_time_steps = len(dyn_map_cube.coord('time').points)
        with cd(dst_folder):
            if not os.path.isdir(png_dir):
                os.mkdir(png_dir)
            number_of_pngs = len(os.listdir(png_dir))
        
        value_range = [
            dyn_map_cube.attributes["presentation_min"],
            dyn_map_cube.attributes["presentation_max"]
        ]
        unit_text = f"{fmt_units(dyn_map_cube.units)}"
        dst = f"./{base_name}.gif"
        with cd(f"{dst_folder}/{png_dir}"):
            for time_step in range(number_of_pngs, number_of_time_steps):
                time_coord = dyn_map_cube[time_step].coord('time')
                date = cftime.num2pydate(time_coord.points[0], time_coord.units.name)
                year = date.strftime("%Y")
                plot_title = f"{_title(dyn_map_cube.long_name)} {year}"
                fig = map_handler(
                    dyn_map_cube[time_step],
                    title=plot_title,
                    value_range=value_range,
                    units=unit_text,
                )
                fig.savefig(f"./{base_name}-{time_step:03}.png", bbox_inches="tight")
                plt.close(fig)   
            images = []
            for file_name in sorted(os.listdir(".")):
                images.append(imageio.imread(file_name))
            imageio.mimsave(f'.{dst}', images, fps=2)

        new_plot = {
            'plot': [dst],
            'long_name': [dyn_map_cube.long_name],
            'title': dyn_map_cube.metadata.attributes["title"],
            'comment': dyn_map_cube.metadata.attributes["comment"],
        }
        return new_plot
