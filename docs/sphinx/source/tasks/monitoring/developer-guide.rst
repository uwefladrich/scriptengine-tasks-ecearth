********************
Developer's Guide
********************

This part summarizes guidelines for extending the monitoring tool.

Code Structure
==============

All monitoring tasks are contained in `scriptengine/tasks/ecearth/monitoring`_.
`helpers`_ contains modules with functions and classes that are needed in multiple, unrelated, processing and presentation tasks.

All monitoring tasks inherit from the generic `ScriptEngine Task`_.
Processing tasks have an inheritance substructure defined by their diagnostic type.
New processing tasks should adhere to these structure: 
Either inherit from the corresponding Diagnostictype class (Scalar, Timeseries, Map, Temporalmap) or create a new one if it is a new diagnostic type.
The Diagnostictype class provides a ``save()`` method that can be reused by all inherited tasks.
This structure is illustrated below:

.. image:: class_diagram.png

To make a task accessible to users, add it to `scriptengine/tasks/ecearth/__init__.py`_.

Logging Policy
==============

Every (monitoring) task is responsible for logging its execution.
In the beginning of ``self.run()`` (after *very few* lines of code), a task **must** call ``self.log_info()`` to log that it is active.
A task **should** write only one ``log_info`` message during execution.
General "progression" statements **must** be ``log_debug`` messages. These **should not** be used sparsely.
If a monitoring task has to abort: It **should** use ``log_warning`` (except if the problem is unexpected) and **must not** use `log_error`.

.. _naming-scheme:

Naming Processing Tasks
=======================

A processing task has a name that appears in multiple places:

    - the Python class
    - the Python module
    - the YAML representation
    - the diagnostics on disk created by it

These all adhere to the same naming scheme: ``variable_component_[domain_op_...]_diagnostictype``.
The Python class uses the name in CamelCase naming convention.
YAML representation, module, and diagnostic on disk use the snake\_case naming convention (see the usage example).

.. csv-table::
   :file: ./naming_scheme.csv
   :widths: 20, 20, 20, 20, 20, 20


*Italic keywords* can be used as placeholders for the keywords they describe.
If a user can select the operation of the domain, use *op* as a placeholder.

The ``domain_op`` combination can be used consecutively, e.g.: ``global_sum_month_max_year_mean``.
The variable keyword is less standardized, e.g. amocstrength, sypd, tos, 2t, 167,...
Depending on the diagnostic/processing task, parts of the naming scheme are unnecessary.
``diagnostictype`` may not be omitted.

Usage Example: Naming Scheme
#############################

    - Python class: ``NemoGlobalMeanYearMeanTimeseries``
    - Python module: ``nemo_global_mean_year_mean_timeseries``
    - YAML representation: ``ece.nemo_global_mean_year_mean_timeseries``
    - the diagnostics on disk created by it: ``ece.mon.tos_nemo_global_mean_year_mean_timeseries.nc``

Naming Presentation Tasks
=========================

Naming presentation tasks is not as standardized as for processing tasks.
The task/class/module name should be the presentation outlet, e.g. Markdown.
Their YAML representation is preceded by *ece.mon.presentation* to make them distinguishable from processing tasks.

.. _`scriptengine/tasks/ecearth/monitoring`: https://github.com/uwefladrich/scriptengine-tasks-ecearth/tree/master/scriptengine/tasks/ecearth/monitoring
.. _`ScriptEngine Task`: https://github.com/uwefladrich/scriptengine/blob/master/scriptengine/tasks/base/task.py
.. _`scriptengine/tasks/ecearth/__init__.py`: https://github.com/uwefladrich/scriptengine-tasks-ecearth/tree/master/scriptengine/tasks/ecearth/__init__.py