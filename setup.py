"""setup.py for package scriptengine-tasks-ecearth."""
import os
import codecs
import setuptools

def read(rel_path):
    """
    Helper function to read file in relative path.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()

def get_version(rel_path):
    """
    Helper function to get package version.
    """
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

setuptools.setup(
    name="scriptengine-tasks-ecearth",
    version=get_version("scriptengine/tasks/ecearth/version.py"),
    author="Uwe Fladrich, Valentina Schueller",
    author_email="uwe.fladrich@protonmail.com, valentina.schueller@gmail.com",
    description="ScriptEngine tasks for use with the EC-Earth climate model",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/uwefladrich/scriptengine-tasks-ecearth",
    packages=[
        "helpers",
        "scriptengine.tasks.ecearth",
        "scriptengine.tasks.ecearth.monitoring",
        "tests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "scriptengine>=0.6",
        "pyYAML>=5.1",
        "numpy>=1.16.1",
        "imageio>=2.0",
        "scitools-iris>=2.4",
        "cartopy>=0.18",
        "iris-grib>=0.15",
        "python-redmine",
    ],
)
