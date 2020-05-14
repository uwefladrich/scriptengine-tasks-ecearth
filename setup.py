import os
import codecs
import setuptools

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

setuptools.setup(
    name="ece-4-monitoring",
    version=get_version("scriptengine/tasks/monitoring/version.py"),
    author="Valentina Schueller",
    author_email="valentina.schueller@gmail.com",
    description="ScriptEngine tasks for monitoring the EC-Earth climate model",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/valentinaschueller/ece-4-monitoring",
    packages=[
        "helpers",
        "scriptengine.tasks.monitoring",
        "tests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "scriptengine>=0.5",
        "pyYAML>=5.1",
        "netCDF4>=1.5"
    ],
)