"""Helper module to plot Iris monitoring cubes."""

import iris.quickplot as qplt


def format_title(name, units=None):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ").title()
    unit_text = format_units(units)
    if unit_text and unit_text != "1":
        title += " / {}".format(unit_text)
    return title

def format_units(units):
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
