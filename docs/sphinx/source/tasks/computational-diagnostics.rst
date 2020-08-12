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
- data_units (default: 1)
- coord_units (default: 1)
- coord_name (default: 'time')
- coord_bounds (default: [coord_value - 1, coord_value])

	- list with two elements
	- elements can be int/float/double or date/datetime


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
        title: "Some Diagnostic"
        data_value: "{{some_value}}"
        coord_value: "{{leg_num}}"
        dst: "{{mondir}}/some-diagnostic.nc"
        comment: "Diagnostic Description."
        data_units: "m"
        coord_units: "1"
        coord_name: "Leg Number"
        coord_bounds:
            - "{{leg_num - 1}}"
            - "{{leg_num}}"


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
