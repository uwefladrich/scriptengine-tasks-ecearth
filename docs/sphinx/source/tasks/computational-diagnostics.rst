******************
Scalar Diagnostics
******************

Write Scalar
============

Diagnostic Type: Scalar

::

    - ece.mon.write_scalar:
        long_name: "Experiment ID"
        value: "{{exp_id}}"
        dst: "{{mondir}}/exp-id.yml"

Disk Usage
==========

Diagnostic Type: Scalar

::

    - ece.mon.disk_usage:
        src: "{{rundir}}/output"
        dst: "{{mondir}}/output-disk-usage.yml"

Simulated Years
===============

Diagnostic Type: Scalar

::

    - ece.mon.sim_years:
        dst: "{{mondir}}/sim-years.yml"
        start: "{{start}}"
        end: "{{leg.end}}"


Simulated Legs
==============

Diagnostic Type: Scalar

::

    - ece.mon.sim_legs:
        src: "{{rundir}}"
        dst: "{{mondir}}/sim-legs.yml"

Simulated Years per Day
=======================

Diagnostic Type: Time Series

::

    - ece.mon.sypd:
        leg_start: "{{leg.start}}"
        leg_end: "{{leg.end}}"
        elapsed_time: "{{model_elapsed_time}}"
        leg_num: "{{leg_num}}"
        dst: "{{mondir}}/sypd.nc"