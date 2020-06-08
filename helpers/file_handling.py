"""Helper module for handling files."""

import os
import yaml
import numpy as np
import iris
from iris.experimental.equalise_cubes import equalise_attributes

# Using https://stackoverflow.com/revisions/13197763/9
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

# unnecessary
def filename(mon_id, destination):
    """Creates the file name for a diagnostic."""
    mon_id = "-".join(mon_id.split())
    return f"{destination}/{mon_id}"

# unnecessary
def convert_to_yaml(diagnostic, destination):
    """Converts a diagnostic dictionary to a YAML file."""
    try:
        mon_id = diagnostic["mon_id"]
    except (TypeError, KeyError):
        mon_id = ""
    
    with open(f"{filename(mon_id, destination)}.yml", 'w') as outfile:
        yaml.dump(diagnostic, outfile, sort_keys=False)

def get_month_from_src(month, path_list):
    """
    function to get path for desired month from path_list
    """
    for path in path_list:
        if path[-5:-3] == month:
            return path
    raise FileNotFoundError(f"Month {month} not found in {path_list}!")

def compute_spatial_weights(domain_src, array_shape):
    "Compute weigths for spatial averaging"
    domain_cfg = iris.load(domain_src)
    cell_areas = domain_cfg.extract('e1t')[0][0] * domain_cfg.extract('e2t')[0][0]
    cell_weights = np.broadcast_to(cell_areas.data, array_shape)
    return cell_weights

def compute_month_weights(monthly_data_cube):
    """Compute weights for the different month lengths"""
    time_dim = monthly_data_cube.coord('time', dim_coords=True)
    month_lengths = np.array([bound[1] - bound[0] for bound in time_dim.bounds])
    return month_lengths

def load_input_cube(src, varname):
    """Load input files into one cube."""
    month_cubes = iris.load(src, varname)
    equalise_attributes(month_cubes) # 'timeStamp' and 'uuid' would cause ConcatenateError
    leg_cube = month_cubes.concatenate_cube()
    return leg_cube