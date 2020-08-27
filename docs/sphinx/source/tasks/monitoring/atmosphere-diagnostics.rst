**********************
Atmosphere Diagnostics
**********************

These processing tasks assume that the provided input files are GRIB output files from OpenIFS. Further assumptions:

- regularly-spaced in time
- reduced Gaussian grid
- currently only GG output files

OifsGlobalMeanYearMeanTimeseries
================================

Diagnostic Type: Time Series

Mapped to: ``ece.mon.oifs_global_mean_year_mean_timeseries``

::

    - ece.mon.oifs_global_mean_year_mean_timeseries:
        src: "{{gg_files}}"
        dst: "{{mondir}}/2t_oifs_global_mean_year_mean_timeseries.nc"
        grib_code: 167


OifsAllMeanMap
==============

Diagnostic Type: Map

Map Type: global atmosphere

Mapped to: ``ece.mon.oifs_all_mean_map``

::

    - ece.mon.oifs_all_mean_map:
        src: "{{gg_files}}"
        dst: "{{mondir}}/2t_oifs_all_mean_map.nc"
        grib_code: 167

OifsYearMeanTemporalmap
=======================

Diagnostic Type: Temporal Map

Map Type: global atmosphere

Mapped to: ``ece.mon.oifs_year_mean_temporalmap``

::

    - ece.mon.oifs_year_mean_temporalmap:
        src: "{{gg_files}}"
        dst: "{{mondir}}/2t_oifs_year_mean_temporalmap.nc"
        grib_code: 167