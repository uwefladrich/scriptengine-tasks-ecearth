*************************
Computational Diagnostics
*************************

Scalar
=======

Diagnostic Type: Scalar

::

    - ece.mon.scalar:
        title: "Experiment ID"
        value: "{{exp_id}}"
        dst: "{{mondir}}/expid_scalar.yml"

DiskusageRteScalar
==================

Diagnostic Type: Scalar

::

    - ece.mon.diskusage_rte_scalar:
        src: "{{rundir}}/output"
        dst: "{{mondir}}/diskusage_rte_scalar.yml"

SimulatedyearsRteScalar
=======================

Diagnostic Type: Scalar

::

    - ece.mon.simulatedyears_rte_scalar:
        start: "{{start}}"
        end: "{{leg.end}}"
        dst: "{{mondir}}/simulatedyears_rte_scalar.yml"


Timeseries
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

    - ece.mon.timeseries:
        title: "Some Diagnostic"
        data_value: "{{some_value}}"
        coord_value: "{{leg_num}}"
        dst: "{{mondir}}/diagnostic_timeseries.nc"
        
Elaborate Example
#################

::

    - ece.mon.timeseries:
        title: "An Interesting Title"
        data_value: "{{some_value}}"
        coord_value: "{{some_other_value}}"
        dst: "{{mondir}}/diagnostic_timeseries.nc"
        comment: "Diagnostic Description."
        coord_name: "x-axis label"
        coord_units: "s"
        data_name: "y-axis label"
        data_units: "m"


SYPD Example
############

::

    - ece.mon.timeseries:
        title: "Simulated Years per Day"
        coord_value: "{{leg_num}}"
        coord_name: "Leg Number"
        comment: "SYPD development during this simulation."
        data_value: "{{((schedule.leg.end - schedule.leg.start)/script_elapsed_time/365)}}"
        dst: "{{mondir}}/sypd_timeseries.nc"

