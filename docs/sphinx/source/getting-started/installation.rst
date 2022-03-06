************
Installation
************

The ScriptEngine tasks for EC-Earth require a Unix(-like) operating system and Python 3.6+.

The package supports two different installation methods:

    * Installation using conda and PyPI/pip;
    * Installation from source.

The next sections will detail the procedure to install the package for both methods.

You can check if everything worked out by calling ``se --help`` from the command line.
ScriptEngine will show all registered tasks, and the tasks in this package start with the prefix ``ece.``.

.. highlight:: bash

Installation using conda and pip
================================

This is the recommended way to install this package.

Get the conda package manager following the `instructions`_ for your operating system. 
Create an environment and activate it with 

::

    conda create --name your_environment_name python=3.6 # or 3.7 or 3.8
    conda activate your_environment_name

Alternatively, activate the existing conda environment you want to use for this package.

Update your conda environment using the file ``conda_environment.yml`` in the GitHub repository::

    conda env update -n your_environment_name --file conda_environment.yml

This YAML file contains necessary dependencies for packages that *should* be installed via conda (like, e.g., Iris).
You can also install these packages from source, but this will require a lot more attention during the setup process. 
Refer to the documentation of the packages in ``conda_environment.yml`` for more information on installing them.

The ScriptEngine tasks for EC-Earth can then be installed using

::

    pip install scriptengine-tasks-ecearth

The remaining dependencies will be installed automatically.


Installation from Source
========================

You can download or clone the source code from https://github.com/uwefladrich/scriptengine-tasks-ecearth.

Update your conda environment using the file ``conda_environment.yml`` in the GitHub repository::

    conda env update -n your_environment_name --file conda_environment.yml

This YAML file contains necessary dependencies for packages that *should* be installed via conda (like, e.g., Iris).
You can also install these packages from source, but this will require a lot more attention during the setup process. 
Refer to the documentation of the packages in ``conda_environment.yml`` for more information on installing them.

The package can be installed from inside the *scriptengine-tasks-ecearth* directory (assuming you did not choose a different name) using

::

    pip install -e .

If you want to run the tests, you will need to download the `test data`_, put the files into ``tests/testdata``, 
and install Pytest_.
You can run them from inside the *scriptengine-tasks-ecearth* directory using

:: 

    pytest .

To build the documentation manually, you will need Sphinx_.
The HTML theme is the `Read the Docs Sphinx Theme`_.

.. _instructions: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _test data: https://github.com/valentinaschueller/ece-4-monitoring-test-data
.. _Pytest: https://docs.pytest.org/en/latest
.. _Sphinx: https://www.sphinx-doc.org/
.. _Read the Docs Sphinx Theme:  https://sphinx-rtd-theme.readthedocs.io/en/stable/index.html
