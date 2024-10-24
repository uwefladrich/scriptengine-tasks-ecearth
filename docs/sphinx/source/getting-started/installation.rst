************
Installation
************

The ScriptEngine tasks for EC-Earth require a Unix(-like) operating system and
Python 3.

The package supports two different installation methods:

    * installation using conda;
    * installation from source.

The sections below will detail the procedure to install the package for
both of the above recommended methods.

Packages for the ScriptEngine tasks are also provided at PyPI and can be
installed with with pip, but a number of dependencies are only available as
conda packages, and installing from PyPI needs manual installation of this
dependencies.

Once the installation is done, you can check if everything worked out by calling
``se --help`` from the command line. ScriptEngine will show all registered
tasks, and the tasks in this package start with the prefix ``ece.``.


Installation Using Conda
========================

.. note::
    This is the recommended way to install this package for users.

Get the conda package manager following the `instructions`_ for your operating
system. Create an environment and activate it with::

    conda create --name <ENVIRONMENT_NAME> python>=3.8
    conda activate <ENVIRONMENT_NAME>

Alternatively, activate an existing conda environment you want to use for this
package.

After activating the conda environment, ScriptEngine tasks for EC-Earth can be
installed using::

    conda install scriptengine-tasks-ecearth

All dependencies will be installed in the process. In particular, ScriptEngine
will be installed.


Installation from Source
========================

You can download or clone the source code from `GitHub
<https://github.com/uwefladrich/scriptengine-tasks-ecearth>`_.

Update your conda environment using the file ``conda_environment.yml`` in the
Git repository::

    conda env update -n <ENVIRONMENT_NAME> --file conda_environment.yml

which will install all dependencies (like, e.g., Iris). You can also install
these packages from source, but this will require a lot more attention during
the setup process. Refer to the documentation of the packages in
``conda_environment.yml`` for more information on installing them.

The package can be installed from inside the ``scriptengine-tasks-ecearth``
directory (assuming you did not choose a different name) using::

    pip install -e .

If you want to run the tests, you will need to download the `test data`_, put
the files into ``tests/testdata``, and install Pytest_ (``conda install
pytest``). You can run them from inside the ``scriptengine-tasks-ecearth``
directory using::

    pytest .

To build the documentation manually, you will need Sphinx_.
The HTML theme is the `Read the Docs Sphinx Theme`_.

.. _instructions: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _test data: https://github.com/valentinaschueller/ece-4-monitoring-test-data
.. _Pytest: https://docs.pytest.org/en/latest
.. _Sphinx: https://www.sphinx-doc.org/
.. _Read the Docs Sphinx Theme:  https://sphinx-rtd-theme.readthedocs.io/en/stable/index.html
