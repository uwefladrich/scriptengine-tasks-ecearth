import codecs
from pathlib import Path

import setuptools


def read(rel_path):
    """
    Helper function to read file in relative path.
    """
    here = Path(__file__).parent.resolve()
    with codecs.open(here / rel_path, "r") as fp:
        return fp.read()


def get_version(rel_path):
    """
    Helper function to get package version.
    """
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]


setuptools.setup(
    name="scriptengine-tasks-ecearth",
    version=get_version("version.py"),
    author="Valentina Schueller, Uwe Fladrich",
    author_email="valentina.schueller@gmail.com, uwe.fladrich@protonmail.com",
    description="ScriptEngine tasks for use with the EC-Earth climate model",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/uwefladrich/scriptengine-tasks-ecearth",
    packages=[
        "helpers",
        "monitoring",
        "tests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "scriptengine>=0.8.1",
        "pyYAML>=5.1",
        "matplotlib>=3.1",
        "numpy>=1.18",
        "imageio>=2.18",
        "scitools-iris>=3.1,!=3.2.0,!=3.2.0.post0",
        "cartopy>=0.20",
        "python-redmine",
    ],
    entry_points={
        "scriptengine.tasks": [
            "ece.mon.scalar = monitoring.scalar:Scalar",
            "ece.mon.timeseries = monitoring.timeseries:Timeseries",
            "ece.mon.diskusage_rte_scalar = monitoring.diskusage_rte_scalar:DiskusageRteScalar",
            "ece.mon.simulatedyears_rte_scalar = monitoring.simulatedyears_rte_scalar:SimulatedyearsRteScalar",
            "ece.mon.nemo_global_mean_year_mean_timeseries = monitoring.nemo_global_mean_year_mean_timeseries:NemoGlobalMeanYearMeanTimeseries",
            "ece.mon.nemo_all_mean_map = monitoring.nemo_all_mean_map:NemoAllMeanMap",
            "ece.mon.nemo_month_mean_temporalmap = monitoring.nemo_time_mean_temporalmap:NemoMonthMeanTemporalmap",
            "ece.mon.nemo_year_mean_temporalmap = monitoring.nemo_time_mean_temporalmap:NemoYearMeanTemporalmap",
            "ece.mon.si3_hemis_sum_month_mean_timeseries = monitoring.si3_hemis_sum_month_mean_timeseries:Si3HemisSumMonthMeanTimeseries",
            "ece.mon.si3_hemis_point_month_mean_all_mean_map = monitoring.si3_hemis_point_month_mean_all_mean_map:Si3HemisPointMonthMeanAllMeanMap",
            "ece.mon.si3_hemis_point_month_mean_temporalmap = monitoring.si3_hemis_point_month_mean_temporalmap:Si3HemisPointMonthMeanTemporalmap",
            "ece.mon.oifs_all_mean_map = monitoring.oifs_all_mean_map:OifsAllMeanMap",
            "ece.mon.oifs_year_mean_temporalmap = monitoring.oifs_year_mean_temporalmap:OifsYearMeanTemporalmap",
            "ece.mon.oifs_global_mean_year_mean_timeseries = monitoring.oifs_global_mean_year_mean_timeseries:OifsGlobalMeanYearMeanTimeseries",
            "ece.mon.presentation.markdown = monitoring.markdown:Markdown",
            "ece.mon.presentation.redmine = monitoring.redmine:Redmine",
            "ece.mon.linear_combination = monitoring.linear_combination:LinearCombination",
        ]
    },
)
