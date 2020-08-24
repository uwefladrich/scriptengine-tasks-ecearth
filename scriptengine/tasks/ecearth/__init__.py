""" ScriptEngine EC-Earth tasks

This module provides SE tasks for the EC-Earth ESM
"""

from .monitoring.simulatedyears_rte_scalar import SimulatedyearsRteScalar
from .monitoring.scalar import Scalar
from .monitoring.markdown_output import MarkdownOutput
from .monitoring.global_average import GlobalAverage
from .monitoring.diskusage_rte_scalar import DiskusageRteScalar
from .monitoring.ice_time_series import SeaIceTimeSeries
from .monitoring.ocean_map import OceanMap
from .monitoring.ocean_time_map import OceanTimeMap
from .monitoring.oifs_all_mean_map import OifsAllMeanMap
from .monitoring.atmosphere_time_map import AtmosphereTimeMap
from .monitoring.ice_map import SeaIceMap
from .monitoring.ice_time_map import SeaIceTimeMap
from .monitoring.atmosphere_time_series import AtmosphereTimeSeries
from .monitoring.timeseries import Timeseries
from .monitoring.redmine_output import RedmineOutput
from .slurm import Sbatch

def task_loader_map():
    return {
        'sbatch': Sbatch,
        'ece.mon.simulatedyears_rte_scalar': SimulatedyearsRteScalar,
        'ece.mon.scalar': Scalar,
        'ece.mon.markdown_report': MarkdownOutput,
        'ece.mon.global_avg': GlobalAverage,
        'ece.mon.diskusage_rte_scalar': DiskusageRteScalar,
        'ece.mon.ice_time_series': SeaIceTimeSeries,
        'ece.mon.ocean_map': OceanMap,
        'ece.mon.ocean_time_map': OceanTimeMap,
        'ece.mon.oifs_all_mean_map': OifsAllMeanMap,
        'ece.mon.atmosphere_time_map': AtmosphereTimeMap,
        'ece.mon.ice_map': SeaIceMap,
        'ece.mon.ice_time_map': SeaIceTimeMap,
        'ece.mon.atmosphere_ts': AtmosphereTimeSeries,
        'ece.mon.time_series': Timeseries,
        'ece.mon.redmine_output': RedmineOutput
        }
