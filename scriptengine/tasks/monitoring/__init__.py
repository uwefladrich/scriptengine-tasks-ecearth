from .simulated_legs import SimulatedLegs
from .simulated_years import SimulatedYears
from .write_scalar import WriteScalar
from .markdown_output import MarkdownOutput
from .global_average import GlobalAverage

def task_loader_map():
    return {
        'ece.mon.sim_legs': SimulatedLegs,
        'ece.mon.sim_years': SimulatedYears,
        'ece.mon.write_scalar': WriteScalar,
        'ece.mon.markdown_report': MarkdownOutput,
        'ece.mon.global_avg': GlobalAverage,
        }
