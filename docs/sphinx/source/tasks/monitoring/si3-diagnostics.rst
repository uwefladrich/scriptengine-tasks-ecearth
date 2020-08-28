*******************
Sea-Ice Diagnostics
*******************

The processing tasks in this chapter create diagnostics for the SI3 sea ice model.

Assumptions about input data:

* input data are output files from SI3, i.e. NetCDF files on a global curvilinear grid.
* data for land cells is flagged as invalid.
* monthly output files. Otherwise the tasks will fail to compute the diagnostics.

.. highlight:: yaml

Si3HemisSumMonthMeanTimeseries
==============================

| Diagnostic Type: Time Series
| Mapped to: ``ece.mon.si3_hemis_sum_month_mean_timeseries``

Computes the hemispheric sum of a sea ice variable's month mean, resulting in a time series diagnostic.
This can be used to create a seasonal cycle time series (March-September or similar) or the time series of another selection of months.

**Required arguments**

* ``src``: A list of strings or a single string containing paths to the desired SI3 output file(s).
* ``domain``: A string containing the path to the ``domain.nc`` file. The variables ``e1t`` and ``e2t`` are used for computing the area weights.
* ``varname``: The name of the ice variable as saved in the output file. Can be ``sivolu`` or ``siconc``.
* ``hemisphere``: The name of the requested hemisphere. Can be ``north`` or ``south``.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.

::

    - ece.mon.si3_hemis_sum_month_mean_timeseries:
        src:
            - "{{feb_file}}"
            - "{{sep_file}}"
        domain: "{{rundir}}/domain_cfg.nc"
        dst: "{{mondir}}/siarea_si3_south_sum_feb+sep_mean_timeseries.nc"
        hemisphere: south
        varname: siconc


Si3HemisPointMonthMeanAllMeanMap
================================

| Diagnostic Type: Map
| Mapped to: ``ece.mon.si3_hemis_point_month_mean_all_mean_map``
| Map Type: polar ice sheet

Computes the simulation average climatology of a sea ice variable's month mean on one hemisphere, resulting in a map diagnostic.
E.g. the simulation mean of all March means of the arctic sea ice concentration.

**Required arguments**

* ``src``: A string containing paths to the desired SI3 output file.
* ``varname``: The name of the ice variable as saved in the output file. Can be ``sivolu`` or ``siconc``.
* ``hemisphere``: The name of the requested hemisphere. Can be ``north`` or ``south``.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.

::

    - ece.mon.si3_hemis_point_month_mean_all_mean_map:
        src: "{{ice_file_sep}}"
        dst: "{{mondir}}/sivolu_si3_north_point_sep_mean_all_mean_map.nc"
        hemisphere: south
        varname: sivolu

Si3HemisPointMonthMeanTemporalmap
=================================

| Diagnostic Type: Temporal Map
| Mapped to: ``ece.mon.si3_hemis_point_month_mean_temporalmap``
| Map Type: polar ice sheet

Creates a temporal map of a sea ice variable's month mean, resulting in a temporal map diagnostic.
E.g. the March means of the arctic sea ice concentration over time.

**Required arguments**

* ``src``: A string containing paths to the desired SI3 output file.
* ``varname``: The name of the ice variable as saved in the output file. Can be ``sivolu`` or ``siconc``.
* ``hemisphere``: The name of the requested hemisphere. Can be ``north`` or ``south``.
* ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.

::

    - ece.mon.si3_hemis_point_month_mean_temporalmap:
            src: "{{ice_file_mar}}"
            dst: "{{mondir}}/siconc_si3_north_point_mar_mean_temporalmap.nc"
            hemisphere: north
            varname: siconc 