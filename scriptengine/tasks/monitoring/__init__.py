from .simulated_years import SimulatedYears
from .markdown_output import MarkdownOutput
from .sst_average import SSTAverage

def task_loader_map():
    return {
        'ec.mon.sim_years': SimulatedYears,
        'ec.mon.markdown_report': MarkdownOutput,
        'ec.mon.global_avg': SSTAverage,
        }
