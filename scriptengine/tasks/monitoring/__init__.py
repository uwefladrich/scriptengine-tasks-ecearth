from .simulated_years import SimulatedYears
from .markdown_output import MarkdownOutput
from .sst_average import SSTAverage

def task_loader_map():
    return {
        'simulated_years': SimulatedYears,
        'markdown_output': MarkdownOutput,
        'sst_average': SSTAverage,
        }
