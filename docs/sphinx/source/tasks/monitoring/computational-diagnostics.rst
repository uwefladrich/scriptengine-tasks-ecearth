**************************************
Computational Performance Diagnostics
**************************************

The processing tasks in this chapter create diagnostics informing about computational performance and the general experiment progress.

.. highlight:: yaml

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

.. _sypd-using-timeseries:

SYPD using Timeseries
======================

::

    - ece.mon.timeseries:
        title: "Simulated Years per Day"
        coord_value: "{{leg_num}}"
        coord_name: "Leg Number"
        comment: "SYPD development during this simulation."
        data_value: "{{((schedule.leg.end - schedule.leg.start)/script_elapsed_time/365)}}"
        dst: "{{mondir}}/sypd_timeseries.nc"
