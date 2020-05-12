"""Generic Structure of a Processing Task"""

from scriptengine.tasks.base import Task

class Processor(Task):
    def __init__(self, parameters):
        super().__init__(__name__, parameters)
        self.mon_id = "Processor Task"
    
    def run(self, context):
        # get file from correct directory
        # do something with data from that file
        # create a MonitoringDict object
        # mon_dict = MonitoringDict(context, self.mon_id)
        # save data in MonitoringDict object
        # create appropriate file from object (mon_dict.convert_to_file())
        pass