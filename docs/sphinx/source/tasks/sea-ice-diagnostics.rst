*******************
Sea-Ice Diagnostics
*******************

Sea-Ice Time Series
========================

Diagnostic Type: Time Series

Mapped to: ``ece.mon.ice_time_series``

varname can be ``sivolu`` or ``siconc``.

::

    - ece.mon.ice_time_series:
        summer: "{{feb_file}}"
        summer: "{{sep_file}}"
        domain: "{{rundir}}/domain_cfg.nc"
        dst: "{{mondir}}/siarea-south.nc"
        hemisphere: south
        varname: sivolu


Si3HemisPointMonthMeanAllMeanMap
================================

Diagnostic Type: Map

Mapped to: ``ece.mon.si3_hemis_point_month_mean_all_mean_map``

varname can be ``sivolu`` or ``siconc``.

Map Type: polar ice sheet

::

    - ece.mon.si3_hemis_point_month_mean_all_mean_map:
        src: "{{ice_file_sep}}"
        dst: "{{mondir}}/sivolu_si3_north_point_sep_mean_all_mean_map.nc"
        hemisphere: south
        varname: sivolu

Sea-Ice Time Map
================

Diagnostic Type: Time Map

Mapped to: ``ece.mon.ice_time_map``

varname can be ``sivolu`` or ``siconc``.

Map Type: polar ice sheet

::

    - ece.mon.ice_time_map:
            src: "{{ice_file_mar}}"
            dst: "{{mondir}}/siconc-north-mar.nc"
            hemisphere: north
            varname: siconc 