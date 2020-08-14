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
        src: "{{ice_files}}"
        domain: "{{rundir}}/domain_cfg.nc"
        dst: "{{mondir}}/siarea-south.nc"
        hemisphere: south
        varname: sivolu


Sea-Ice Volume per Area Map
===========================

Diagnostic Type: Map

Mapped to: ``ece.mon.sithic_static_map``

Map Type: polar ice sheet

::

    - ece.mon.sithic_static_map:
        src: "{{ice_file_sep}}"
        dst: "{{mondir}}/sithic-south-sep.nc"
        hemisphere: south

Sea-Ice Time Map
================

Diagnostic Type: Time Map

Mapped to: ``ece.mon.ice_dynamic_map``

varname can be ``sivolu`` or ``siconc``.

Map Type: polar ice sheet

::

    - ece.mon.ice_dynamic_map:
            src: "{{ice_file_mar}}"
            dst: "{{mondir}}/siconc-north-mar.nc"
            hemisphere: north
            varname: siconc 