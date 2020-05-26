"""Visualization Task that saves Data and Plots to a Markdown File."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
import jinja2
import os, glob
import yaml
import iris
import iris.quickplot as qplt 
import matplotlib.pyplot as plt

class MarkdownOutput(Task):
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super().__init__(__name__, parameters, required_parameters=required)
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src}, {self.dst})"
        )

    def run(self, context):
        self.src = [j2render(input_file, context) 
                    for input_file in self.src]
        self.dst = j2render(self.dst, context)

        self.scalars = []
        self.nc_plots = []
        for path in self.src:
            if path.endswith('.yml'):
                try:
                    with open(path) as yml_file: 
                        dct = yaml.load(yml_file, Loader = yaml.FullLoader)
                    self.scalars.append(dct)
                except FileNotFoundError:
                    self.log_warning(f"FileNotFoundError: Ignoring {path}.")
            elif path.endswith('.nc'):
                self.plot_netCDF(path)
            else:
                self.log_warning(f"{path} does not end in .nc or .yml. Ignored.")
                
        
        env = jinja2.Environment(loader=jinja2.PackageLoader('ece-4-monitoring'))
        md_template = env.get_template('monitoring.md.j2')
        
        with open(f"{self.dst}", 'w') as md_out:
            md_out.write(md_template.render(
                scalar_diagnostics = self.scalars,
                nc_diagnostics = self.nc_plots,
            ))
    
    def plot_netCDF(self, path):
        try:
            cubes = iris.load(path)
            if len(cubes) == 1:
                plot_path = f"{path}.png" 
                self.plot_cube(cubes[0], plot_path)
                self.nc_plots.append({
                    'plot': [plot_path],
                    'long_name': [cube.long_name],
                    'title': cube.metadata.attributes["title"],
                    'comment': cube.metadata.attributes["comment"],
                })
            else:
                plot_list = []
                ln_list = []
                for count, cube in enumerate(cubes):
                    plot_path = f"{path}-{count}.png"
                    long_name = cube.long_name
                    self.plot_cube(cube, plot_path)
                    plot_list.append(plot_path)
                    ln_list.append(long_name)
                self.nc_plots.append({
                    'plot': plot_list,
                    'long_name': ln_list,
                    'title': cubes[0].metadata.attributes["title"],
                    'comment': cubes[0].metadata.attributes["comment"],
                })
        except IOError:
            self.log_warning(f"IOError, file not found: Ignoring {path}.")
    
    def plot_cube(self, cube, dst):
        qplt.plot(cube, '.-')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(dst)
        qplt.plt.close() 
        self.log_debug(f"New plot created at {dst}.")