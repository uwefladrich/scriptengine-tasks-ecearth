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

.. TODO: go over this part, especially the examples!

| Diagnostic Type: Timeseries/Map/Temporalmap (does not work with YAML files)
| Mapped to: ``ece.mon.linear_combination``

This processing task creates a linear combination of different, compatible NetCDF variables :math:`v_i`, i.e., :math:`\sum_i \alpha_i v_i`.
It can be used for custom diagnostics, e.g., computing the difference of precipitation and evaporation.
It can make sense to create the linear combination before or after calling one of the other processing tasks.

**Required arguments**

* ``src``: A list of dictionaries containing the ``path``, ``varname``, and optional ``factor`` :math:`\alpha_i` (default is 1.0).
* ``dst``: Dictionary containing information about the destination file. Must contain the ``path`` (ending in *.nc*) where the target can be stored.

**Optional arguments of ``dst``**

If these arguments are not provided, the task will use the defaults determined by Iris.

* ``varname``: The name of the target variable which can be used to access it later on.
* ``longname``: The `long name` of the target variable.
* ``standardname``: A `valid standard name` for the target variable as defined by the `CF conventions`.
* ``unit``: Custom target unit for the destination file. Can be one of the UDUNITS_ strings (see the :ref:`above note on checking valid units <check-valid-units>`).

Minimal Example
###############

::

    - ece.mon.linear_combination:
        src:
            - path: "oifs_output_file.nc"
              varname: "rsnt"
            - path: "oifs_output_file.nc"
              varname: "rlnt"
        dst:
            - path: "rsnt+rlnt.nc"

Elaborate Example
#################

::

    - ece.mon.linear_combination:
        src:
            - path: "oifs_output_file.nc"
              varname: p
              factor: 1.0
            - path: "oifs_output_file.nc"
              varname: e
              factor: -1.0
        dst:
            path: "p-e.nc"
            varname: "p-e" # TODO does +/- work inside a varname?
            longname: "Precipitation minus evaporation"
            standardname: precipitation_amount
            unit: "kg m-2"

.. _UDUNITS: https://www.unidata.ucar.edu/software/udunits/
.. _valid standard name: http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
.. _CF conventions: http://cfconventions.org/Data/cf-conventions/cf-conventions-1.9/cf-conventions.html#standard-name
.. _long name: http://cfconventions.org/Data/cf-conventions/cf-conventions-1.9/cf-conventions.html#long-name