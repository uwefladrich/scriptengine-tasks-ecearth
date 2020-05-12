"""
Converter functions for the EC-Earth 4 Monitoring Tasks
"""
import yaml
import netCDF4

class MonitoringDict(dict):
    def __init__(self, context, mon_id, ):
        self['exp_id'] = context.get('exp_id','----')
        self['mon_id'] = mon_id
        self['data'] = {
                'dimensions': {},
                'values': {},
            }

    def filename(self):
        """Creates the appropriate file name for a monitoring dictionary"""
        mon_id = "-".join(self["mon_id"].split())
        return mon_dict["exp_id"] + "-" + mon_id
    

    def convert_to_yaml(self):
        """Converts a monitoring dictionary to a YAML file."""
        with open(f"{self.filename()}.yml", 'w') as outfile:
            yaml.dump(self, outfile, sort_keys=False)


    def convert_to_nc(self):
        """Converts a monitoring dictionary to a netCDF file."""
        outfile = netCDF4.Dataset(f'{self.filename()}.nc', 'w')
        for k,v in self.items():
            if k is not "data":
                outfile.setattr(k, v)
        #TODO: take care of data items
    


#test_dict = {"exp_id": "TEST", 
#            "mon_id": "simulated years", 
#            "data": {"time": [0,1,2], 
#                "years": [55, 56, 57],},
#            }
#convert_to_yaml(test_dict)
#convert_to_nc(test_dict)