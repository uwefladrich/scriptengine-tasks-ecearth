**************************************
Generic Processing Tasks
**************************************

The processing tasks in this chapter are not tied to a specific EC-Earth component.

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

Timeseries
=======================

| Diagnostic Type: Timeseries
| Mapped to: ``ece.mon.timeseries``

This processing task creates a time series diagnostic, illustrating the progression of a scalar quantity over the duration of the current experiment.
It can be used for custom output, an exemplary use case is the SYPD time series, a computational performance diagnostic: :ref:`sypd-using-timeseries`.

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

.. _check-valid-units:

.. note:: To check if a unit string is compatible with UDUNITS, use the following small Python check:

    .. code-block:: python

        import cf_units
        cf_units.as_unit("kg") # insert your test string here
    
    This will throw a `ValueError` in case the unit is not compatible with UDUNITS_.

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


LinearCombination
=================

| Diagnostic Type: Timeseries/Map/Temporalmap (does not work with YAML files)
| Mapped to: ``ece.mon.linear_combination``

This processing task computes a linear combination :math:`\sum \alpha_i v_i` of
scalar factors :math:`\alpha_i` and compatible NetCDF variables :math:`v_i`, and
writes the result into a new NetCDF file. This can be used to create custom
diagnostics, for example the difference or (weighted) sum of variables. The
resulting NetCDF files and variables can be used in subsequent processing tasks.
Note that the ``LinearCombination`` task does not perform any spatial or
temporal averaging.

Example use cases for ``LinearCombination`` include the computation of
precipitation minus evaporation (mass balance :math:`P-E`) and energy balances
by summing up individual radiation contributions.

The input variables for the ``LinearCombination`` task must be compatible in
terms of dimensions and units, according to the rules of `Iris cube maths`_. If
Iris cannot compute the linear combination, the execution of the task is aborted
with an error explaining the type of incompatibility.

**Required arguments**

* ``src``: A list of dictionaries, each containing the ``path``, ``varname``,
  for each variable, and an optional scalar ``factor`` :math:`\alpha_i`. The
  default ``factor`` is 1.0.
* ``dst``: A dictionary describing the NetCDF file used to store the custom
  diagnostic. Must at least contain the ``path`` and ``varname`` for the result.

**Optional ``dst`` arguments**

* ``longname``: The `long name` of the target variable. If not provided, the
  resulting diagnostic will not have a longname.
* ``standardname``: A `valid standard name` for the target variable as defined
  by the `CF conventions`. If not provided, the resulting diagnostic will not
  have a standardname.
* ``unit``: Custom target unit for the destination file. Can be one of the
  UDUNITS_ strings (see the :ref:`above note on checking valid units
  <check-valid-units>`).
  If not provided, Iris will try to determine the unit of the linear
  combination.

Examples
########

The first example adds short and long wave radiation contributions to provide an
energy budget at the top of atmosphere (TOA)::

    - ece.mon.linear_combination:
        src:
          - varname: rsnt
            path: oifs_output_file.nc
          - varname: rlnt
            path: oifs_output_file.nc
        dst:
          varname: net_toa
          longname: Net TOA
          path: net_toa.nc

The second example computes the difference between precipitation :math:`P` and
evaporation :math:`E` to provide the mass balance :math:`P-E` as custom
diagnostic in ``pme.nc``. Note that the standardname and unit are explicitely
set for the output NetCDF file::

    - ece.mon.linear_combination:
        src:
          - varname: pr
            path: oifs_output_file.nc
          - varname: evspsbl
            path: oifs_output_file.nc
            factor: -1.0
        dst:
          varname: pme
          longname: "Precipitation - Evaporation"
          standardname: precipitation_amount
          unit: "kg m-2"
          path: pme.nc

.. _UDUNITS: https://www.unidata.ucar.edu/software/udunits/
.. _valid standard name: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
.. _CF conventions: http://cfconventions.org/Data/cf-conventions/cf-conventions-1.9/cf-conventions.html#standard-name
.. _long name: http://cfconventions.org/Data/cf-conventions/cf-conventions-1.9/cf-conventions.html#long-name
.. _Iris cube maths: https://scitools-iris.readthedocs.io/en/stable/userguide/cube_maths.html
