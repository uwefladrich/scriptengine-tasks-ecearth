*****************
Ocean Diagnostics
*****************

These processing tasks assume that the provided source files are monthly output files of the NEMO ocean modeling component that span one leg of an EC-Earth 4 experiment. One leg can, but does not have to be, one year long.

If the files are not monthly files or do not span the leg (e.g. if files are missing), the processing tasks or Iris might throw some warnings or exceptions.

Global Average Time Series
==========================

Diagnostic Type: Time Series

Mapped to: ``ece.mon.global_average``

This processing task computes the temporal and spatial average of an extensive oceanic quantity as a time series. It then saves it either as a new diagnostic file or appends it to the existing diagnostic file.

A common application is the time series of the annual global mean of the sea surface temperature or sea surface salinity. To compute an annual mean, the leg has to be one year long. If it is, e.g., six months long, the task will compute the six month spatial mean of the input variable.

The required arguments are:

- ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
- ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
- ``domain``: A string containing the path to the ``domain.nc`` file. In this file, the variables ``e1t`` and ``e2t`` are used for computing the area weights.
- ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

run(self, context)
------------------

First, the required arguments get loaded from the context. The processing task returns with a logged error message if ``dst`` does not end in ``.nc``.

The input files get loaded and concatenated into one single Iris cube with a call to ``helpers.load_input_cube()``. Since the variable metadata (standard name, long name, units) is already available in the NEMO output, this will not have to be set separately.

The area weights for the grid cells get computed from the domain file using ``helpers.compute_spatial_weights()``. These are used to collapse the cube along its latitude and longitude coordinates. Since these coordinates are two-dimensional on a curvilinear grid, Iris would throw warnings "Collapsing a multi-dimensional coordinate". These get suppressed by the processing task.

NEMO output files contain an auxiliary time coordinate, this makes collapsing along the time axis more difficult. Thus, this coordinate gets removed before averaging over time. 
The time mean is also weighted based on the month lengths. These weights get computed by ``helpers.compute_time_weights()``. A dimension coordinate becomes a scalar coordinate when collapsing the cube along it. Since the diagnostic needs a time axis (as it is a time series with multiple values), the time axis needs to be promoted to a dimension coordinate again after averaging over time.

The ``run()``-method calls ``helpers.set_metadata()`` to add relevant metadata to the diagnostic. Finally, it calls the ``save_cube()`` method to save the cube.

save_cube(self, new_cube, dst)
------------------------------

This method saves the newly computed global average cube in a NetCDF file. If this file does not exist yet, the cube can be saved using ``iris.save()`` without anything else to do. 

If the file exists already, it gets loaded as an Iris cube. The new cube should get appended to the existing diagnostic on disk. This should not happen if appending would lead to a non-monotonic time axis. This can happen when monitoring leg n+1 finishes before monitoring leg n is completed. When inserting would lead to a non-monotonic time axis for the diagnostic on disk, the cube will not get saved and a warning message will get logged.
When a monotonic insert is possible, the two cubes (existing diagnostic at ``dst`` and ``new_cube``) get concatenated. Since overwriting Iris cubes currently in memory leads to file corruption, the new version of the diagnostic gets saved as a copy, the old version gets deleted, and the new version is renamed.

Usage Example
-------------

::

    - ece.mon.global_average:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos-time-series.nc"
        domain: "{{rundir}}/domain.nc"
        varname: "tos"


Ocean Map
=========

Diagnostic Type: Map
Map Type: global ocean

Mapped to: ``ece.mon.ocean_map``

This task computes the simulation average of the spatial distribution of an oceanic variable. This results in a map of the global ocean. First, it calculates the time mean of the current leg. If no old version of the simulation average exists, the new annual mean gets saved as the simulation average. Otherwise, the old simulation average and new annual mean get merged into a new simulation average, the old diagnostic on disk is then replaced.

An application is the simulation average map of the sea surface temperature or sea surface salinity. Simulation average means "from the beginning of the experiment until now". This processing task assumes monthly output files but the leg length is completely irrelevant.

The required arguments are:

- ``src``: A list of strings containing paths to the desired NEMO output files. This list can be manually entered or (often better) created by the ``find`` task.
- ``dst``: A string ending in ``.nc``. This is where the diagnostic will be saved.
- ``varname``: The name of the oceanic variable as it is saved in the NEMO output file.

run(self, context)
------------------

First, the required arguments get loaded from the context. The processing task returns with a logged error message if ``dst`` does not end in ``.nc``.

The input files get loaded and concatenated into one single Iris cube with a call to ``helpers.load_input_cube()``. Since the variable metadata (standard name, long name, units) is already available in the NEMO output, this will not have to be set separately.

NEMO output files contain an auxiliary time coordinate, this makes collapsing along the time axis more difficult. Thus, this coordinate gets removed before averaging over time. The time mean is weighted based on the month lengths. These weights get computed by ``helpers.compute_time_weights()``.

The ``run()``-method calls ``helpers.set_metadata()`` to add relevant metadata to the diagnostic. Finally, it calls the ``save_cube()`` method to save the cube.

save_cube(self, new_average, dst)
------------------------------------------

This method saves the newly computed leg average cube in a NetCDF file. If this file exists already, the new simulation average gets computed first and saved afterwards.

If the file exists already, it gets loaded as an Iris cube. The new cube should get appended to the existing diagnostic on disk. This should not happen if appending would lead to a non-monotonic time axis. This can happen when monitoring leg n+1 finishes before monitoring leg n is completed. When inserting would lead to a non-monotonic time axis for the diagnostic on disk, the cube will not get saved and a warning message will get logged.
When a monotonic insert is possible, the two cubes (existing diagnostic at ``dst`` and ``new_cube``) get concatenated. Then, ``compute_simulation_avg()`` computes the new simulation average. Since overwriting Iris cubes currently in memory leads to file corruption, the new version of the diagnostic gets saved as a copy, the old version gets deleted, and the new version is renamed.

Usage Example
-------------

::

    - ece.mon.ocean_map:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos-climatology.nc"
        varname: "tos"


Ocean Time Map
==============

Diagnostic Type: Time Map
Map Type: global ocean

Mapped to: ``ece.mon.ocean_time_map``

::

    - ece.mon.ocean_time_map:
        src: "{{t_files}}"
        dst: "{{mondir}}/tos-annual-map.nc"
        varname: "tos"