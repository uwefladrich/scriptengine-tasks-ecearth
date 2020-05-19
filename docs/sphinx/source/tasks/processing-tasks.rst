****************
Monitoring Tasks
****************

Each diagnostic used to monitor an EC-Earth run is implemented as a ScriptEngine Task. 
More precisely, they can be referred to as *Processing Tasks*.
The other set of Monitoring Tasks is used to present the diagnostics in an appropriate manner. 
These are called *Visualization Tasks*.

For EC-Earth monitoring, these two areas are always separated:
    * The creation, computation and extension of data related to one monitoring diagnostic is dealt with in a Processing Task.
    * The visualization of output files of the Processing Tasks is bundled in few, customizable Visualization Tasks.

This separation allows a user or developer

1. to look at and interact with non-visualized data,
2. to choose their own visualization tools for diagnostics,
3. and to visualize their own data.

Processing Tasks
################

A Processing Task can be seen as the implementation concept of a single monitoring diagnostic. There is currently no enforcement for what a Processing Task must produce in the end. However, a certain structure of a Processing Task's run()-method is recommended:

1. Get the data used to compute the diagnostic - i.e., find the correct file(s) in the output folder.
2. Compute the monitoring diagnostic.
3. Parse the diagnostic, including appropriate metadata, to a netCDF or YAML file named "exp_id-monitoring-id". This file can be used by visualization tasks.
