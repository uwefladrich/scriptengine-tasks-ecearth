"""setup.py for package scriptengine-tasks-ecearth."""
import os
import codecs
import setuptools

def read(rel_path):
    """
    Helper function to read file in relative path.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
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
    version=get_version("scriptengine/tasks/ecearth/version.py"),
    author="Uwe Fladrich, Valentina Schueller",
    author_email="uwe.fladrich@protonmail.com, valentina.schueller@gmail.com",
    description="ScriptEngine tasks for use with the EC-Earth climate model",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/uwefladrich/scriptengine-tasks-ecearth",
    packages=[
        "helpers",
        "scriptengine.tasks.ecearth",
        "scriptengine.tasks.ecearth.monitoring",
        "tests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "scriptengine>=0.7.1",
        "pyYAML>=5.1",
        "numpy>=1.16.1",
        "imageio>=2.0",
        "scitools-iris>=3",
        "cartopy>=0.18",
        "iris-grib>=0.15",
        "python-redmine",
    ],
    entry_points={
        'scriptengine.tasks': [
            'ece.mon.scalar = scriptengine.tasks.ecearth.monitoring.scalar:Scalar',
            'ece.mon.timeseries = scriptengine.tasks.ecearth.monitoring.timeseries:Timeseries',
            'ece.mon.diskusage_rte_scalar = scriptengine.tasks.ecearth.monitoring.diskusage_rte_scalar:DiskusageRteScalar',
            'ece.mon.simulatedyears_rte_scalar = scriptengine.tasks.ecearth.monitoring.simulatedyears_rte_scalar:SimulatedyearsRteScalar',
            'ece.mon.nemo_global_mean_year_mean_timeseries = scriptengine.tasks.ecearth.monitoring.nemo_global_mean_year_mean_timeseries:NemoGlobalMeanYearMeanTimeseries',
            'ece.mon.nemo_all_mean_map = scriptengine.tasks.ecearth.monitoring.nemo_all_mean_map:NemoAllMeanMap',
            'ece.mon.nemo_month_mean_temporalmap = scriptengine.tasks.ecearth.monitoring.nemo_time_mean_temporalmap:NemoMonthMeanTemporalmap',
            'ece.mon.nemo_year_mean_temporalmap = scriptengine.tasks.ecearth.monitoring.nemo_time_mean_temporalmap:NemoYearMeanTemporalmap',
            'ece.mon.si3_hemis_sum_month_mean_timeseries = scriptengine.tasks.ecearth.monitoring.si3_hemis_sum_month_mean_timeseries:Si3HemisSumMonthMeanTimeseries',
            'ece.mon.si3_hemis_point_month_mean_all_mean_map = scriptengine.tasks.ecearth.monitoring.si3_hemis_point_month_mean_all_mean_map:Si3HemisPointMonthMeanAllMeanMap',
            'ece.mon.si3_hemis_point_month_mean_temporalmap = scriptengine.tasks.ecearth.monitoring.si3_hemis_point_month_mean_temporalmap:Si3HemisPointMonthMeanTemporalmap',
            'ece.mon.oifs_all_mean_map = scriptengine.tasks.ecearth.monitoring.oifs_all_mean_map:OifsAllMeanMap',
            'ece.mon.oifs_year_mean_temporalmap = scriptengine.tasks.ecearth.monitoring.oifs_year_mean_temporalmap:OifsYearMeanTemporalmap',
            'ece.mon.oifs_global_mean_year_mean_timeseries = scriptengine.tasks.ecearth.monitoring.oifs_global_mean_year_mean_timeseries:OifsGlobalMeanYearMeanTimeseries',
            'ece.mon.presentation.markdown = scriptengine.tasks.ecearth.monitoring.markdown:Markdown',
            'ece.mon.presentation.redmine = scriptengine.tasks.ecearth.monitoring.redmine:Redmine',
        ]
    }
)
