"""
Converter functions for the EC-Earth 4 Monitoring Tasks
"""
import yaml

def convert_to_yaml(mon_dict):
    """Converts a monitoring dictionary to a YAML file."""
    mon_id = "-".join(mon_dict["mon_id"].split())
    fname = mon_dict["exp_id"] + "-" + mon_id

    with open(f"{fname}.yml", 'w') as outfile:
        yaml.dump(mon_dict, outfile, sort_keys=False)


def convert_to_nc(mon_dict):
    """Converts a monitoring dictionary to a netCDF file."""
    pass


# test_dict = {"exp_id": "TEST", "mon_id": "simulated years", "data": 55}
# convert_to_yaml(test_dict)