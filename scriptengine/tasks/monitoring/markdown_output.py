from scriptengine.tasks.base import Task
import jinja2
import os, glob
import yaml

class MarkdownOutput(Task):
    def __init__(self, parameters):
        required = [
            "exp_id",
            "src",
            "dst"
        ]
        super().__init__(__name__, parameters, required_parameters=required)
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.exp_id})"
        )

    def run(self, context):
        # Find all YAML files with the experiment ID
        os.chdir(f"{self.src}")
        filepaths = [f"{self.src}/{filename}" for filename in glob.glob(f"{self.exp_id}-*.yml")]
        scalars = []
        for path in filepaths:
            with open(path) as file: 
                dct = yaml.load(
                    file,
                    Loader = yaml.FullLoader,
                )
                scalars.append(dct)
        
        print(scalars)
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('ece-4-monitoring'),
            )

        md_template = env.get_template('monitoring.md.j2')
        
        with open(f"{self.dst}/monitoring.md", 'w') as md_out:
            md_out.write(md_template.render(
                exp_id = self.exp_id,
                scalar_diagnostics = scalars,
            ))
