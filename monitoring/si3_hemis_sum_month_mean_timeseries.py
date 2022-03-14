"""Processing Task that calculates the seasonal cycle of sea ice variables in one leg."""

import warnings

import cf_units
import iris
import numpy as np
from scriptengine.tasks.core import timed_runner

import helpers.cubes
import helpers.nemo

from .timeseries import Timeseries

_meta_dict = {
    "sivolu": {
        "long_name": "Sea-Ice Volume",
        "standard_name": "sea_ice_volume",
        "var_name": "sivol",
        "old_unit": "m3",
        "new_unit": "1e3 km3",
    },
    "siconc": {
        "long_name": "Sea-Ice Area",
        "standard_name": "sea_ice_area",
        "var_name": "siarea",
        "old_unit": "m2",
        "new_unit": "1e6 km2",
    },
}


def _remove_aux_time(cube):
    try:
        aux_time = cube.coord("time", dim_coords=False)
    except iris.exceptions.CoordinateNotFoundError:
        pass
    else:
        cube.remove_coord(aux_time)
    return cube


_month_names = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def _month_number(month):
    "Returns number of month (1..12) for month (int or string)"
    nums = dict()
    # Allow all of "January", "january", "jan", 1
    for num, name in enumerate(_month_names):
        nums[name] = nums[num + 1] = nums[name[:3]] = nums[name.lower()] = num + 1
    try:
        return nums[month]
    except KeyError:
        raise ValueError(f"Invalid month: '{month}'")


def _month_name(month):
    return _month_names[_month_number(month) - 1]


def _extract_month(cube, month):
    return cube.extract(
        iris.Constraint(time=lambda cell: cell.point.month == _month_number(month))
    )


def _mask_other_hemisphere(cube, hemisphere):
    lats = cube.coord("latitude").points
    if hemisphere.lower() in ("south", "s"):
        cube.data = np.ma.masked_where(lats > 0, cube.data)
    elif hemisphere.lower() in ("north", "n"):
        cube.data = np.ma.masked_where(lats < 0, cube.data)
    else:
        raise ValueError("Invalid hemisphere, must be 'north' or 'south'")
    return cube


def _yearly_time_bounds(cube):

    t_coord = cube.coord("time")
    cube.remove_coord("time")

    t_point = t_coord.units.num2date(t_coord.points[0])
    t_first, t_last = (
        t_coord.units.date2num(t_point.replace(month=1, day=1)),
        t_coord.units.date2num(t_point.replace(year=t_point.year + 1, month=1, day=1)),
    )
    cube.add_aux_coord(
        iris.coords.DimCoord(
            t_coord.points,
            bounds=np.array([[t_first, t_last]]),
            standard_name=t_coord.standard_name,
            long_name=t_coord.long_name,
            units=t_coord.units,
            var_name=t_coord.var_name,
            attributes=t_coord.attributes,
        )
    )
    return iris.util.new_axis(cube, "time")


def _set_cell_methods(cube, hemisphere):
    """Set the correct cell methods."""
    cube.cell_methods = ()
    cube.add_cell_method(iris.coords.CellMethod("point", coords="time"))
    cube.add_cell_method(
        iris.coords.CellMethod(
            "sum", coords="area", intervals=f"{hemisphere}ern hemisphere"
        )
    )
    return cube


class Si3HemisSumMonthMeanTimeseries(Timeseries):
    """Si3HemisSumMonthMeanTimeseries Processing Task"""

    _required_arguments = (
        "src",
        "dst",
        "domain",
        "hemisphere",
        "varname",
        "month",
    )

    def __init__(self, arguments):
        Si3HemisSumMonthMeanTimeseries.check_arguments(arguments)
        super().__init__(
            {**arguments, "title": None, "coord_value": None, "data_value": None}
        )

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = self.getarg("dst", context)
        varname = self.getarg("varname", context)
        hemisphere = self.getarg("hemisphere", context)
        month = self.getarg("month", context)
        domain = self.getarg("domain", context)

        self.log_info(
            f"Create {varname} time series for {hemisphere}ern hemisphere at {dst}."
        )
        self.log_debug(f"Domain: {domain}, source file: {src}")

        try:
            long_name = _meta_dict[varname]["long_name"]
        except KeyError:
            self.log_warning(
                (
                    f"Invalid varname argument: '{varname}', must be one of {_meta_dict.keys()}."
                    " Diagnostic will not be included!"
                )
            )
            return

        if hemisphere not in ("north", "south"):
            self.log_warning(
                (
                    f"Invalid hemisphere argument '{hemisphere}', must be 'north' or 'south'."
                    " Diagnostic will not be included!"
                )
            )
            return
        self.check_file_extension(dst)

        this_leg = helpers.cubes.load_input_cube(src, varname)
        this_leg = _remove_aux_time(this_leg)
        this_leg = _extract_month(this_leg, month)
        this_leg = _mask_other_hemisphere(this_leg, hemisphere)
        this_leg = _yearly_time_bounds(this_leg)

        with warnings.catch_warnings():
            # Suppress warning about insufficient metadata.
            warnings.filterwarnings(
                "ignore",
                "Collapsing a multi-dimensional coordinate.",
                UserWarning,
            )
            this_leg_summed = this_leg.collapsed(
                ["latitude", "longitude"],
                iris.analysis.SUM,
                weights=helpers.nemo.spatial_weights(this_leg, domain, "T"),
            )

        this_leg_summed.standard_name = _meta_dict[varname]["standard_name"]
        this_leg_summed.units = cf_units.Unit(_meta_dict[varname]["old_unit"])
        this_leg_summed.convert_units(_meta_dict[varname]["new_unit"])
        this_leg_summed.long_name = (
            f"{long_name} {_month_name(month)} {hemisphere.capitalize()}"
        )
        this_leg_summed.var_name = _meta_dict[varname]["var_name"] + hemisphere[0]

        metadata = {
            "comment": (
                f"Area weighted sum of {long_name} / **{varname}** on the {hemisphere}ern hemisphere."
            ),
            "title": f"{long_name} ({_month_name(month)} mean on the {hemisphere}ern hemisphere)",
        }
        this_leg_summed = helpers.cubes.set_metadata(this_leg_summed, **metadata)
        this_leg_summed = _set_cell_methods(this_leg_summed, hemisphere)
        self.save(this_leg_summed, dst)
