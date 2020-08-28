*************************
General Structure
*************************

The monitoring tool has a defined workflow: At the end of each leg, using EC-Earth output, it creates relevant diagnostics.
These diagnostics are then visualized in an expressive manner.
Both the selection of diagnostics as well as the desired visualization might vary between experiments and are thus configurable.
The software consists of two different task types: 

**Processing tasks** process input from the model output and the runtime environment.
With this, they create diagnostics and save them in a file. 

**Presentation tasks** read these saved diagnostics and visualize them.
Then, they present all diagnostics at a presentation outlet.

Diagnostic Types!
Reference to Naming Scheme!

