import yaml
import netCDF4

"""File handling functions. Not necessary anymore."""

def filename(mon_id, destination):
    """Creates the file name for a diagnostic."""
    mon_id = "-".join(mon_id.split())
    return f"{destination}/{mon_id}"
    

def convert_to_yaml(diagnostic, destination):
    """Converts a diagnostic dictionary to a YAML file."""
    try:
        mon_id = diagnostic["mon_id"]
    except (TypeError, KeyError):
        mon_id = ""
    
    with open(f"{filename(mon_id, destination)}.yml", 'w') as outfile:
        yaml.dump(diagnostic, outfile, sort_keys=False)


#def convert_to_nc(diagnostic, destination):
#    """Converts a diagnostic dictionary to a netCDF file."""
#    outfile = netCDF4.Dataset(f'{filename(diagnostic, destination)}.nc', 'w')
#    for k,v in diagnostic.items():
#        if k is not "data":
#            outfile.setattr(k, v)
#    #TODO: take care of data items
#    outfile.close()