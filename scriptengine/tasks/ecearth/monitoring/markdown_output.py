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
from helpers.cube_plot import ts_plot

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
                try:
                    with open(path) as yml_file:
                        dct = yaml.load(yml_file, Loader=yaml.FullLoader)
                    scalars.append(dct)
                except FileNotFoundError:
                    self.log_warning(f"FileNotFoundError: Ignoring {path}.")
            elif path.endswith('.nc'):
                nc_plots = self.plot_netcdf(nc_plots, path, dst)
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
        if "_se_ocwd" in context:
            search_path.extend([context["_se_ocwd"],
                                os.path.join(context["_se_ocwd"], "templates")])
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

    def plot_netcdf(self, nc_plots, path, dst_folder):
        try:
            cubes = iris.load(path)

            # get file name without extension
            base_name = os.path.splitext(os.path.basename(path))[0]

            if len(cubes) == 1:
                dst_file = f"./{base_name}.png"
                self.plot_cube(cubes[0], dst_folder, dst_file)
                nc_plots.append({
                    'plot': [dst_file],
                    'long_name': [cubes[0].long_name],
                    'title': cubes[0].metadata.attributes["title"],
                    'comment': cubes[0].metadata.attributes["comment"],
                })
            else:
                plot_list = []
                ln_list = []
                for cube in cubes:
                    dst_file = f"./{base_name}-{cube.var_name}.png"
                    long_name = cube.long_name
                    self.plot_cube(cube, dst_folder, dst_file)
                    plot_list.append(dst_file)
                    ln_list.append(long_name)
                nc_plots.append({
                    'plot': plot_list,
                    'long_name': ln_list,
                    'title': cubes[0].metadata.attributes["title"],
                    'comment': cubes[0].metadata.attributes["comment"],
                })
        except IOError:
            self.log_warning(f"IOError, file not found: Ignoring {path}.")
        return nc_plots

    def plot_cube(self, cube, folder, file):
        ts_plot(cube)
        with cd(folder):
            plt.savefig(file, bbox_inches="tight")
        plt.close()
        self.log_debug(f"New plot created at {folder}.")
