"""Helper module for handling files."""

import os
import yaml

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
