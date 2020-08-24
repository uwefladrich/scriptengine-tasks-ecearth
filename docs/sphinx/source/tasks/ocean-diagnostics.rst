*****************
Ocean Diagnostics
*****************

These processing tasks assume that the provided source files are monthly output files of the NEMO ocean modeling component that span one leg of an EC-Earth 4 experiment. One leg can, but does not have to be, one year long.

If the files are not monthly files or do not span the leg (e.g. if files are missing), the processing tasks or Iris might throw some warnings or exceptions.

NemoGlobalMeanYearMeanTimeseries
================================

Diagnostic Type: Time Series

Mapped to: ``ece.mon.nemo_global_mean_year_mean_timeseries``

This processing task computes the temporal and spatial average of an extensive oceanic quantity as a time series.
It then saves it either as a new diagnostic file or appends it to the existing diagnostic file.

A common application is the time series of the annual global mean of the sea surface temperature or sea surface salinity.
To compute an annual mean, the leg has to be one year long. If it is, e.g., six months long, the task will compute the six month spatial mean of the input variable.

The required arguments are:

- ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
- ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
- ``domain``: A string containing the path to the ``domain.nc`` file. In this file, the variables ``e1t`` and ``e2t`` are used for computing the area weights.
- ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

Usage Example
-------------

::

    - ece.mon.nemo_global_mean_year_mean_timeseries:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_global_mean_year_mean_timeseries.nc"
        domain: "{{rundir}}/domain.nc"
        varname: "tos"


NemoAllMeanMap
==============

Diagnostic Type: Map
Map Type: global ocean

Mapped to: ``ece.mon.nemo_all_mean_map``

::

    - ece.mon.nemo_all_mean_map:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_all_mean_map.nc"
        varname: "tos"


NemoYearMeanTemporalMap
=======================

Diagnostic Type: Temporal Map
Map Type: global ocean

Mapped to: ``ece.mon.nemo_year_mean_temporalmap``

::

    - ece.mon.nemo_year_mean_temporalmap:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_year_mean_temporalmap.nc"
        varname: "tos"


NemoMonthMeanTemporalMap
========================

Diagnostic Type: Temporal Map
Map Type: global ocean

Mapped to: ``ece.mon.nemo_month_mean_temporalmap``

::

    - ece.mon.nemo_month_mean_temporalmap:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_month_mean_temporalmap.nc"
        varname: "tos"