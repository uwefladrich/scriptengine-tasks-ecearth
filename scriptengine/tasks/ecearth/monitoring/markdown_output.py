"""Presentation Task that saves Data and Plots to a Markdown File."""

import os
import jinja2
import yaml
import iris
import matplotlib.pyplot as plt

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
from scriptengine.jinja import filters as j2filters
from helpers.file_handling import cd
from helpers.cube_plot import plot_time_series, plot_static_map, plot_dynamic_map
import helpers.exceptions as exceptions

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
                scalars = self.load_yaml(path, scalars)
            elif path.endswith('.nc'):
                nc_plots = self.load_netcdf(path, dst, nc_plots)
            else:
                self.log_warning(f"{path} does not end in .nc or .yml. Ignored.")

        try:
            exp_id_index = next(
                (index for (index, d) in enumerate(scalars) if d["long_name"] == "Experiment ID"),
                None,
                )
            scalars.insert(0, scalars.pop(exp_id_index))
        except TypeError: # TypeError if exp_id_index == None
            self.log_debug('No scalar with long_name "Experiment ID" given.')

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
                ))
    
    def load_yaml(self, yaml_path, scalar_dict):
        try:
            with open(yaml_path) as yml_file:
                loaded_dict = yaml.load(yml_file, Loader=yaml.FullLoader)
            return scalar_dict.append(loaded_dict)
        except FileNotFoundError:
            self.log_warning(f"FileNotFoundError: Ignoring {yaml_path}.")
            return scalar_dict
        


    def load_netcdf(self, path, dst_folder, nc_plots):
        """
        Load netCDF file and determine diagnostic type.
        """
        try:
            cubes = iris.load(path)
        except IOError:
            self.log_warning(f"IOError, file not found: Ignoring {path}.")
            return nc_plots
        
        if cubes[0].attributes['type'] == 'time series':
            new_plots = self.load_time_series(cubes, path, dst_folder)
        elif cubes[0].attributes['type'] == 'map':
            new_plots = self.load_map(cubes, path, dst_folder)
        
        nc_plots.append(new_plots)
        return nc_plots

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
    
    def load_map(self, cube_list, path, dst_folder):
        """
        Load map diagnostic and determine map type.
        """
        self.log_debug(f"Loading map diagnostic {path}")
        # get file name without extension
        base_name = os.path.splitext(os.path.basename(path))[0]
        plot_list = []
        long_name_list = []
        for cube in cube_list:
            if cube.var_name.endswith('_sim_avg'):
                self.log_debug(f"New static map: {cube.var_name}")
                try:
                    new_plot_path = plot_static_map(cube, dst_folder, base_name)
                except exceptions.InvalidMapTypeException as msg:
                    self.log_warning(f"Invalid Map Type: {msg}")
            else:
                self.log_debug(f"New dynamic map: {cube.var_name}")
                try:
                    new_plot_path = plot_dynamic_map(cube, dst_folder, base_name)
                except exceptions.InvalidMapTypeException as msg:
                    self.log_warning(f"Invalid Map Type: {msg}")
            plot_list.append(new_plot_path)
            long_name_list.append(cube.long_name)

        new_plots = {
            'plot': plot_list,
            'long_name': long_name_list,
            'title': cube_list[0].metadata.attributes["title"],
            'comment': cube_list[0].metadata.attributes["comment"],
        }
        return new_plots
