""" ScriptEngine EC-Earth tasks

This module provides SE tasks for the EC-Earth ESM
"""

from .monitoring.simulatedyears_rte_scalar import SimulatedyearsRteScalar
from .monitoring.scalar import Scalar
from .monitoring.markdown import Markdown
from .monitoring.nemo_global_mean_year_mean_timeseries import NemoGlobalMeanYearMeanTimeseries
from .monitoring.diskusage_rte_scalar import DiskusageRteScalar
from .monitoring.si3_hemis_sum_month_mean_timeseries import Si3HemisSumMonthMeanTimeseries
from .monitoring.nemo_all_mean_map import NemoAllMeanMap
from .monitoring.nemo_time_mean_temporalmap import NemoYearMeanTemporalmap, NemoMonthMeanTemporalmap
from .monitoring.oifs_all_mean_map import OifsAllMeanMap
from .monitoring.oifs_year_mean_temporalmap import OifsYearMeanTemporalmap
from .monitoring.si3_hemis_point_month_mean_all_mean_map import Si3HemisPointMonthMeanAllMeanMap
from .monitoring.si3_hemis_point_month_mean_temporalmap import Si3HemisPointMonthMeanTemporalmap
from .monitoring.oifs_global_mean_year_mean_timeseries import OifsGlobalMeanYearMeanTimeseries
from .monitoring.timeseries import Timeseries
from .monitoring.redmine import Redmine
from .slurm import Sbatch

def task_loader_map():
    return {
        'sbatch': Sbatch,
        'ece.mon.scalar': Scalar,
        'ece.mon.timeseries': Timeseries,
        'ece.mon.diskusage_rte_scalar': DiskusageRteScalar,
        'ece.mon.simulatedyears_rte_scalar': SimulatedyearsRteScalar,
        'ece.mon.nemo_global_mean_year_mean_timeseries': NemoGlobalMeanYearMeanTimeseries,
        'ece.mon.nemo_all_mean_map': NemoAllMeanMap,
        'ece.mon.nemo_month_mean_temporalmap': NemoMonthMeanTemporalmap,
        'ece.mon.nemo_year_mean_temporalmap': NemoYearMeanTemporalmap,
        'ece.mon.si3_hemis_sum_month_mean_timeseries': Si3HemisSumMonthMeanTimeseries,
        'ece.mon.si3_hemis_point_month_mean_all_mean_map': Si3HemisPointMonthMeanAllMeanMap,
        'ece.mon.si3_hemis_point_month_mean_temporalmap': Si3HemisPointMonthMeanTemporalmap,
        'ece.mon.oifs_all_mean_map': OifsAllMeanMap,
        'ece.mon.oifs_year_mean_temporalmap': OifsYearMeanTemporalmap,
        'ece.mon.oifs_global_mean_year_mean_timeseries': OifsGlobalMeanYearMeanTimeseries,
        'ece.mon.presentation.markdown': Markdown,
        'ece.mon.presentation.redmine': Redmine,
        }
