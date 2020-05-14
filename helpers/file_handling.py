import yaml
import netCDF4

def filename(diagnostic, destination):
    """Creates the file name for a diagnostic dictionary."""
    
    try:
        exp_id = diagnostic["exp_id"]
    except (TypeError, KeyError):
        exp_id = ""
    
    try:
        mon_id = "-".join(diagnostic["mon_id"].split())
    except (TypeError, KeyError):
        mon_id = ""
    
    return f"{destination}/{exp_id}-{mon_id}"
    

def convert_to_yaml(diagnostic, destination):
    """Converts a diagnostic dictionary to a YAML file."""
    with open(f"{filename(diagnostic, destination)}.yml", 'w') as outfile:
        yaml.dump(diagnostic, outfile, sort_keys=False)


def convert_to_nc(diagnostic, destination):
    """Converts a diagnostic dictionary to a netCDF file."""
    outfile = netCDF4.Dataset(f'{filename(diagnostic, destination)}.nc', 'w')
    for k,v in diagnostic.items():
        if k is not "data":
            outfile.setattr(k, v)
    #TODO: take care of data items
    outfile.close()