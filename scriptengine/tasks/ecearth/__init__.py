""" ScriptEngine EC-Earth tasks

This module provides SE tasks for the EC-Earth ESM
"""

from .monitoring.simulated_years import SimulatedYears
from .monitoring.scalar import Scalar
from .monitoring.markdown_output import MarkdownOutput
from .monitoring.global_average import GlobalAverage
from .monitoring.disk_usage import DiskUsage
from .monitoring.ice_time_series import SeaIceTimeSeries
from .monitoring.ocean_static_map import OceanStaticMap
from .monitoring.ocean_dynamic_map import OceanDynamicMap
from .monitoring.atmosphere_static_map import AtmosphereStaticMap
from .monitoring.atmosphere_dynamic_map import AtmosphereDynamicMap
from .monitoring.ice_map import SeaIceMap
from .monitoring.ice_dynamic_map import SeaIceDynamicMap
from .monitoring.atmosphere_time_series import AtmosphereTimeSeries
from .monitoring.time_series import TimeSeries
from .monitoring.redmine_output import RedmineOutput
from .slurm import Sbatch

def task_loader_map():
    return {
        'sbatch': Sbatch,
        'ece.mon.sim_years': SimulatedYears,
        'ece.mon.scalar': Scalar,
        'ece.mon.markdown_report': MarkdownOutput,
        'ece.mon.global_avg': GlobalAverage,
        'ece.mon.disk_usage': DiskUsage,
        'ece.mon.ice_time_series': SeaIceTimeSeries,
        'ece.mon.ocean_static_map': OceanStaticMap,
        'ece.mon.ocean_dynamic_map': OceanDynamicMap,
        'ece.mon.atmosphere_static_map': AtmosphereStaticMap,
        'ece.mon.atmosphere_dynamic_map': AtmosphereDynamicMap,
        'ece.mon.ice_map': SeaIceMap,
        'ece.mon.ice_dynamic_map': SeaIceDynamicMap,
        'ece.mon.atmosphere_ts': AtmosphereTimeSeries,
        'ece.mon.time_series': TimeSeries,
        'ece.mon.redmine_output': RedmineOutput
        }
