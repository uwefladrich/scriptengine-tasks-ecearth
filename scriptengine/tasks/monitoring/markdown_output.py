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

        scalars = []
        nc_plots = []
        for path in self.src:
            if path.endswith('.yml'):
                try:
                    with open(path) as yml_file: 
                        dct = yaml.load(yml_file, Loader = yaml.FullLoader)
                    scalars.append(dct)
                except FileNotFoundError:
                    self.log_warning(f"FileNotFoundError: Ignoring {path}.")
            elif path.endswith('.nc'):
                try:
                    cube = iris.load_cube(path)
                    qplt.plot(cube, '.-')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig(f"{path}.png")
                    qplt.plt.close() 
                    nc_plots.append({
                        'plot': f'{path}.png',
                        'long_name': cube.long_name,
                        'title': cube.metadata.attributes["title"],
                        'comment': cube.metadata.attributes["comment"],
                    })
                except IOError:
                    self.log_warning(f"IOError, file not found: Ignoring {path}.")
            else:
                self.log_warning(f"{path} does not end in .nc or .yml. Ignored.")
                
        
        env = jinja2.Environment(loader=jinja2.PackageLoader('ece-4-monitoring'))
        md_template = env.get_template('monitoring.md.j2')
        
        with open(f"{self.dst}", 'w') as md_out:
            md_out.write(md_template.render(
                scalar_diagnostics = scalars,
                nc_diagnostics = nc_plots,
            ))
