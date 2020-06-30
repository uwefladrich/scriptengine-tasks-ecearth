**********************
Atmosphere Diagnostics
**********************

These processing tasks assume that the provided input files are GRIB output files from OpenIFS. Further assumptions:

- regularly-spaced in time
- reduced Gaussian grid
- currently only GG output files

Atmosphere Time Series
======================

Diagnostic Type: Time Series

Mapped to: ``ece.mon.atmosphere_ts``

::

    - ece.mon.atmosphere_ts:
        src: "{{gg_files}}"
        dst: "{{mondir}}/167-time-series.nc"
        grib_code: 167


Atmosphere Map
==============

Diagnostic Type: Map

Map Type: global atmosphere

Mapped to: ``ece.mon.atmosphere_static_map``

::

    - ece.mon.atmosphere_static_map:
        src: "{{gg_files}}"
        dst: "{{mondir}}/167-climatology.nc"
        grib_code: 167

Atmosphere Time Map
===================

Diagnostic Type: Time Map

Map Type: global atmosphere

Mapped to: ``ece.mon.atmosphere_dynamic map``

::

    - ece.mon.atosphere_dynamic_map:
        src: "{{gg_files}}"
        dst: "{{mondir}}/167-annual-map.nc"
        grib_code: 167