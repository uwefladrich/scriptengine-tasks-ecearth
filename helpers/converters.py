"""
Converter functions for the EC-Earth 4 Monitoring Tasks
"""
import yaml
import netCDF4

def filename(mon_dict):
    """Creates the appropriate file name for a monitoring dictionary"""
    mon_id = "-".join(mon_dict["mon_id"].split())
    return mon_dict["exp_id"] + "-" + mon_id
    

def convert_to_yaml(mon_dict):
    """Converts a monitoring dictionary to a YAML file."""
    with open(f"{filename(mon_dict)}.yml", 'w') as outfile:
        yaml.dump(mon_dict, outfile, sort_keys=False)


def convert_to_nc(mon_dict):
    """Converts a monitoring dictionary to a netCDF file."""
    outfile = netCDF4.Dataset(f'{filename(mon_dict)}.nc', 'w')
    for k,v in mon_dict.items():
        if k is not "data":
            outfile.setattr(k, v)
    #TODO: take care of data items
    


test_dict = {"exp_id": "TEST", 
            "mon_id": "simulated years", 
            "data": {"time": [0,1,2], 
                "years": [55, 56, 57],},
            }
convert_to_yaml(test_dict)
#convert_to_nc(test_dict)