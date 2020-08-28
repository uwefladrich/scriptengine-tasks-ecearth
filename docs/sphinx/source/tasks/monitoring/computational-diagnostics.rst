**************************************
Computational Performance Diagnostics
**************************************

The processing tasks in this chapter create diagnostics informing about computational performance and the general experiment progress.

.. highlight:: yaml

Scalar
=======

| Diagnostic Type: Scalar
| Mapped to: ``ece.mon.scalar``

This is the base class for all implemented scalar tasks.
The Scalar processing task writes custom output to a YAML file.

**Required arguments**

* ``title``: Title of the diagnostic
* ``value``: Value of the scalar
* ``dst``: Destination, must end in *.yml* or *.yaml*

**Optional arguments**

* ``comment``: Additional description of diagnostic. Default: ``None``.

::

    - ece.mon.scalar:
        title: "Experiment ID"
        value: "{{exp_id}}"
        dst: "{{mondir}}/expid_scalar.yml"

DiskusageRteScalar
==================

| Diagnostic Type: Scalar
| Mapped to: ``ece.mon.diskusage_rte_scalar``

Computes the size of a user-specified directory.

**Required arguments**

* ``src``: Path to the specified directory.
* ``dst``: Destination, must end in *.yml* or *.yaml*

::

    - ece.mon.diskusage_rte_scalar:
        src: "{{rundir}}/output"
        dst: "{{mondir}}/diskusage_rte_scalar.yml"

SimulatedyearsRteScalar
=======================

| Diagnostic Type: Scalar
| Mapped to: ``ece.mon.simulatedyears_rte_scalar``

Computes the difference in years between ``end`` and ``start``.

**Required arguments**

* ``start``: Start date of the simulation.
* ``end``: End date of the current leg.
* ``dst``: Destination, must end in *.yml* or *.yaml*

::

    - ece.mon.simulatedyears_rte_scalar:
        start: "{{start}}"
        end: "{{leg.end}}"
        dst: "{{mondir}}/simulatedyears_rte_scalar.yml"


Timeseries
=======================

| Diagnostic Type: Time Series
| Mapped to: ``ece.mon.timeseries``

This processing task creates a time series diagnostic, illustrating the progression of a scalar quantity over the duration of the current experiment.
It can be used for custom output, an exemplary use case is the SYPD time series (shown below).

**Required arguments**

* ``title``: Title of the diagnostic
* ``data_value``: Value of the new data point
* ``coord_value``: New value of the time coordinate (can be int/float/double or date/datetime). Must be monotonically increasing.
* ``dst``: Destination, must end in *.nc*

**Optional arguments**

* ``comment``: Additional description of diagnostic. Default: "."
* ``data_name``: Name of the data variable. Default: value of ``title``
* ``data_unit``: Unit of the data variable. Can be one of the UDUNITS_ strings. Default: 1
* ``coord_name``: Name of the coordinate. Default: *time*
* ``coord_unit``: Unit of the coordinate. Can be one of the UDUNITS_ strings. Default: 1

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

.. _UDUNITS: https://www.unidata.ucar.edu/software/udunits/udunits-current/udunits/udunits2-common.xml