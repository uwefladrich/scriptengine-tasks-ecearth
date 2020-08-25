********************
Developer's Guide
********************

This part summarizes guidelines for extending this task set and/or the monitoring tool.

Logging Policy
==============

Every (monitoring) task is responsible for logging its execution.
In the beginning of ``self.run()`` (after *very few* lines of code), a task **must** call ``self.log_info()`` to log that it is active.
A task **should** write only one ``log_info`` message during execution.
General "progression" statements **must** be ``log_debug`` messages. These **should not** be used sparsely.
If a monitoring task has to abort: It **should** use ``log_warning`` (except if the problem is unexpected) and **must not** use `log_error`.