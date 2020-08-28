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

    * For everything to work you need to install the ScriptEngine package (`ScriptEngine on PyPI`_ or `on GitHub`_)
    * The monitoring tool requires PyYAML_, Iris_ and iris-grib_ to open EC-Earth output files. 
    * Additionally, NumPy_, Python-Redmine_ and Imageio_ are required.

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

If you want to run the tests, you will need to install Pytest_.
You can run them from inside the *scriptengine-tasks-ecearth* directory using

:: 

    pytest .

To build the documentation manually, you will need Sphinx_.
The HTML theme is the `Read the Docs Sphinx Theme`_.



.. _ScriptEngine on PyPI: https://pypi.org/project/scriptengine/
.. _on GitHub: https://github.com/uwefladrich/scriptengine
.. _PyYAML: https://pyyaml.org/
.. _Iris: https://scitools.org.uk/iris/docs/latest/
.. _iris-grib: https://github.com/SciTools/iris-grib
.. _NumPy: https://numpy.org/
.. _Python-Redmine: https://python-redmine.com/
.. _Imageio: http://imageio.github.io/
.. _Pytest: https://docs.pytest.org/en/latest
.. _Sphinx: https://www.sphinx-doc.org/
.. _Read the Docs Sphinx Theme:  https://sphinx-rtd-theme.readthedocs.io/en/stable/index.html