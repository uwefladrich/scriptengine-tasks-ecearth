""" ScriptEngine EC-Earth tasks

This module provides SE tasks for the EC-Earth ESM
"""

from .monitoring.simulated_legs import SimulatedLegs
from .monitoring.simulated_years import SimulatedYears
from .monitoring.write_scalar import WriteScalar
from .monitoring.markdown_output import MarkdownOutput
from .monitoring.global_average import GlobalAverage
from .monitoring.disk_usage import DiskUsage
from .monitoring.ice_volume import SeaIceVolume
from .monitoring.ice_area import SeaIceArea
from .slurm import Sbatch

def task_loader_map():
    return {
        'sbatch': Sbatch,
        'ece.mon.sim_legs': SimulatedLegs,
        'ece.mon.sim_years': SimulatedYears,
        'ece.mon.write_scalar': WriteScalar,
        'ece.mon.markdown_report': MarkdownOutput,
        'ece.mon.global_avg': GlobalAverage,
        'ece.mon.disk_usage': DiskUsage,
        'ece.mon.ice_volume': SeaIceVolume,
        'ece.mon.ice_area': SeaIceArea,
        }
