"""Helper module to plot Iris monitoring cubes."""

import os
import imageio

import math
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cftime
import numpy as np

from helpers.file_handling import cd
import helpers.map_type_handling as type_handling
from helpers.exceptions import InvalidMapTypeException

def _title(name, units=None):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ").title()
    unit_text = fmt_units(units)
    if unit_text:
        title += " / {}".format(unit_text)
    return title

def fmt_units(units):
    """Format Cube Units as String"""
    if not (
            units is None
            or units.is_unknown()
            or units.is_no_unit()
        ):
        if qplt._use_symbol(units):
            return units.symbol
        else:
            return units
    else:
        return None