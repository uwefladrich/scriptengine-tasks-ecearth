"""Visualization Task that saves Data and Plots to a Markdown File."""

from scriptengine.tasks.base import Task
from scriptengine.jinja import render as j2render
from helpers.file_handling import cd
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
                self.plot_netCDF(path, self.dst)
            else:
                self.log_warning(f"{path} does not end in .nc or .yml. Ignored.")

        try:  
            exp_id_index = next((index for (index, d) in enumerate(self.scalars) if d["long_name"] == "Experiment ID"), None)      
            self.scalars.insert(0, self.scalars.pop(exp_id_index))
        except:
            pass

        env = jinja2.Environment(loader=jinja2.PackageLoader('ece-4-monitoring'))
        md_template = env.get_template('monitoring.md.j2')
        
        with cd(self.dst):
            with open(f"./summary.md", 'w') as md_out:
                md_out.write(md_template.render(
                    scalar_diagnostics = self.scalars,
                    nc_diagnostics = self.nc_plots,
                ))
    
    def plot_netCDF(self, path, dst_folder):
        try:
            cubes = iris.load(path)

            # get file name without extension
            base_name = os.path.splitext(os.path.basename(path))[0]

            if len(cubes) == 1:
                dst_file = f"./{base_name}.png" 
                self.plot_cube(cubes[0], dst_folder, dst_file)
                self.nc_plots.append({
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
                self.nc_plots.append({
                    'plot': plot_list,
                    'long_name': ln_list,
                    'title': cubes[0].metadata.attributes["title"],
                    'comment': cubes[0].metadata.attributes["comment"],
                })
        except IOError:
            self.log_warning(f"IOError, file not found: Ignoring {path}.")
    
    def plot_cube(self, cube, folder, file):
        qplt.plot(cube, '.-')
        plt.xticks(rotation=45)
        plt.tight_layout()
        with cd(folder):
            plt.savefig(file)
        qplt.plt.close() 
        self.log_debug(f"New plot created at {folder}.")