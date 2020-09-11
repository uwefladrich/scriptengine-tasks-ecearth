*****************
NEMO Diagnostics
*****************

The processing tasks in this chapter create diagnostics for the NEMO ocean model.

Assumptions about input data

* input data are output files from NEMO, i.e. NetCDF files on a global curvilinear grid.
* currently, only 2D variables can be treated.
* it is assumed that data for land cells is flagged as invalid.
* A leg length of one year is expected. Longer/shorter lengths won't lead to failure but file descriptions might be inaccurate (e.g. the *comment* attribute might say "annual mean" despite being a half-year mean).

.. highlight:: yaml

NemoGlobalMeanYearMeanTimeseries
================================

| Diagnostic Type: Time Series
| Mapped to: ``ece.mon.nemo_global_mean_year_mean_timeseries``

This processing task computes the global and temporal average of a 2D oceanic quantity, resulting in a time series diagnostic.

To compute an annual mean, the leg has to be one year long.
If it is, e.g., six months long, the task will compute the six month global mean of the input variable.

**Required arguments**

* ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
* ``domain``: A string containing the path to the ``domain.nc`` file. Used to compute the global mean.
* ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

**Optional arguments**

* ``grid``: The grid type of the desired variable. Can be T, U, V, W. Default: T.

::

    - ece.mon.nemo_global_mean_year_mean_timeseries:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_global_mean_year_mean_timeseries.nc"
        domain: "{{rundir}}/domain.nc"
        varname: tos


NemoAllMeanMap
==============

| Diagnostic Type: Map
| Map Type: global ocean
| Mapped to: ``ece.mon.nemo_all_mean_map``

This task takes the "simulation average climatology" (i.e., a multi-year mean) of a global 2D ocean variable and saves it as a map diagnostic on disk.

**Required arguments**

* ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
* ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

::

    - ece.mon.nemo_all_mean_map:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_all_mean_map.nc"
        varname: "tos"


NemoYearMeanTemporalMap
=======================

| Diagnostic Type: Temporal Map
| Map Type: global ocean
| Mapped to: ``ece.mon.nemo_year_mean_temporalmap``

This task takes the leg mean of a global 2D ocean variable and saves it as a temporal map diagnostic on disk.
It assumes the leg is one year long, which is why it is called "YearMeanTemporalMap".

**Required arguments**

* ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
* ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

::

    - ece.mon.nemo_year_mean_temporalmap:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_year_mean_temporalmap.nc"
        varname: "tos"


NemoMonthMeanTemporalMap
========================

| Diagnostic Type: Temporal Map
| Map Type: global ocean
| Mapped to: ``ece.mon.nemo_month_mean_temporalmap``

Saves consecutive monthly mean maps of a global 2D ocean variable as a temporal map.
This task will fail if the output frequency is not monthly (e.g. daily or annual output).

**Required arguments**

* ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
* ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

::

    - ece.mon.nemo_month_mean_temporalmap:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos_nemo_month_mean_temporalmap.nc"
        varname: "tos"
