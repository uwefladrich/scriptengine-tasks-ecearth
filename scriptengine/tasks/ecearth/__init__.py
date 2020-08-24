""" ScriptEngine EC-Earth tasks

This module provides SE tasks for the EC-Earth ESM
"""

from .monitoring.simulatedyears_rte_scalar import SimulatedyearsRteScalar
from .monitoring.scalar import Scalar
from .monitoring.markdown_output import MarkdownOutput
from .monitoring.global_average import GlobalAverage
from .monitoring.diskusage_rte_scalar import DiskusageRteScalar
from .monitoring.si3_hemis_sum_month_mean_timeseries import Si3HemisSumMonthMeanTimeseries
from .monitoring.ocean_map import OceanMap
from .monitoring.ocean_time_map import OceanTimeMap
from .monitoring.oifs_all_mean_map import OifsAllMeanMap
from .monitoring.oifs_year_mean_temporalmap import OifsYearMeanTemporalmap
from .monitoring.si3_hemis_point_month_mean_all_mean_map import Si3HemisPointMonthMeanAllMeanMap
from .monitoring.si3_hemis_point_month_mean_temporalmap import Si3HemisPointMonthMeanTemporalmap
from .monitoring.oifs_global_mean_year_mean_timeseries import OifsGlobalMeanYearMeanTimeseries
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
        'ece.mon.si3_hemis_sum_month_mean_timeseries': Si3HemisSumMonthMeanTimeseries,
        'ece.mon.ocean_map': OceanMap,
        'ece.mon.ocean_time_map': OceanTimeMap,
        'ece.mon.oifs_all_mean_map': OifsAllMeanMap,
        'ece.mon.oifs_year_mean_temporalmap': OifsYearMeanTemporalmap,
        'ece.mon.si3_hemis_point_month_mean_all_mean_map': Si3HemisPointMonthMeanAllMeanMap,
        'ece.mon.si3_hemis_point_month_mean_temporalmap': Si3HemisPointMonthMeanTemporalmap,
        'ece.mon.oifs_global_mean_year_mean_timeseries': OifsGlobalMeanYearMeanTimeseries,
        'ece.mon.time_series': Timeseries,
        'ece.mon.redmine_output': RedmineOutput
        }
