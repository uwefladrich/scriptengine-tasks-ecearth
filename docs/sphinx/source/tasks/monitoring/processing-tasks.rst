*************************
Processing Tasks
*************************


The Processing Pattern
======================

A processing task has a name that appears in multiple places:

    - the Python class
    - the Python module
    - the YAML representation
    - the diagnostics on disk created by it

These names all adhere to the same naming scheme, the Processing Pattern: ``variable_component_[domain_op_...]_diagnostictype``.
The Python class uses the Processing Pattern in CamelCase naming convention.
YAML representation, module, and diagnostic on disk use the snake\_case naming convention (see the usage example).

.. csv-table::
   :file: ./processing_pattern.csv
   :widths: 20, 20, 20, 20, 20, 20

*Italic keywords* can be used as placeholders for the keywords they describe.
If a user can select the operation of the domain, use *op* as a placeholder.

The ``domain_op`` combination can be used consecutively, e.g.: ``global_sum_month_max_year_mean``.
The variable keyword is less standardized, e.g. amocstrength, sypd, tos, 2t, 167,...
Depending on the diagnostic/processing task, parts of the Processing Pattern are unnecessary.
``diagnostictype`` may not be omitted.

Usage Example: Processing Pattern
#################################

    - Python class: ``NemoGlobalMeanYearMeanTimeseries``
    - Python module: ``nemo_global_mean_year_mean_timeseries``
    - YAML representation: ``ece.nemo_global_mean_year_mean_timeseries``
    - the diagnostics on disk created by it: ``ece.mon.tos_nemo_global_mean_year_mean_timeseries.nc``
