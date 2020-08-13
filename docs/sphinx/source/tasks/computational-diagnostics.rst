*************************
Computational Diagnostics
*************************

Scalar
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

Generic Time Series
=======================

Diagnostic Type: Time Series

Required Parameters:

- title
- data_value
- coord_value (can be int/float/double or date/datetime)
- dst

Optional Parameters:

- comment (default: '.')
- data_name (default: title)
- data_unit (default: 1)
- coord_name (default: 'time')
- coord_unit (default: 1)

Minimal Example
###############

::

    - ece.mon.time_series:
        title: "Some Diagnostic"
        data_value: "{{some_value}}"
        coord_value: "{{leg_num}}"
        dst: "{{mondir}}/some-diagnostic.nc"
        
Elaborate Example
#################

::

    - ece.mon.time_series:
        title: "An Interesting Title"
        data_value: "{{some_value}}"
        coord_value: "{{some_other_value}}"
        dst: "{{mondir}}/some-diagnostic.nc"
        comment: "Diagnostic Description."
        coord_name: "x-axis label"
        coord_units: "s"
        data_name: "y-axis label"
        data_units: "m"


SYPD Example
############

::

    - ece.mon.time_series:
        title: "Simulated Years per Day"
        coord_value: "{{leg_num}}"
        coord_name: "Leg Number"
        comment: "SYPD development during this simulation."
        data_value: "{{((schedule.leg.end - schedule.leg.start)/script_elapsed_time/365)}}"
        dst: "{{mondir}}/generic-sypd.nc"

