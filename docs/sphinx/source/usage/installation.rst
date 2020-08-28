************
Installation
************

The ScriptEngine tasks for EC-Earth require a Unix(-like) operating system and Python 3.6+.

The package supports two different installation methods:

    * Installation using PyPI (see https://pypi.org);
    * Installation from source (source code available at https://github.com/uwefladrich/scriptengine-tasks-ecearth).

The next sections will detail the procedure to install the package for both methods.

Prerequisites
=============

This package requires a couple of preinstalled Python packages:

    * For everything to work you need to install the ScriptEngine package (`PyPI <https://pypi.org/project/scriptengine/>`_ or `GitHub <https://github.com/uwefladrich/scriptengine>`_
    * The monitoring tool requires `PyYAML <https://pyyaml.org/>`, `Iris <https://scitools.org.uk/iris/docs/latest/>`_ and `iris-grib <https://github.com/SciTools/iris-grib>`_ to open EC-Earth output files. 
    * Additionally, `NumPy <https://numpy.org/>`_, `Python-Redmine <https://python-redmine.com/>`_ and `Imageio <http://imageio.github.io/>`_ are required.

Most of these requirements will be automatically installed during the installation process. 
Iris and iris-grib will have to be installed manually, ideally using a Conda environment.
See the respective documentation for more information on that.

Installation using PyPI
=======================

Make sure that Iris and iris-grib are installed before installing from PyPI.
The package can be installed using

::

    pip install scriptengine-tasks-ecearth


Installation from Source
========================

You can download or clone the source code from https://github.com/uwefladrich/scriptengine-tasks-ecearth.
Make sure that Iris and iris-grib are installed before installing the package.
The package can be installed from inside the *scriptengine-tasks-ecearth* directory (assuming you did not choose a different name) using

::

    pip install -e .

If you want to run the tests, you will need to install `Pytest <https://docs.pytest.org/en/latest>`_.
You can run them from inside the *scriptengine-tasks-ecearth* directory using

:: 

    pytest .

To build the documentation manually, you will need `Sphinx <https://www.sphinx-doc.org/>`_.
The HTML theme is the `Read the Docs Sphinx Theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/index.html>`_.