"""Processing Task that creates a 2D time map of sea ice concentration."""

import iris
import numpy as np
from scriptengine.tasks.core import timed_runner

import helpers.cubes

from .temporalmap import Temporalmap

_meta_dict = {
    "sivolu": {
        "long_name": "Sea-Ice Volume per Area",
    },
    "siconc": {
        "long_name": "Sea-Ice Area Fraction",
        "convert_to": "%",
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
    lats = np.broadcast_to(cube.coord("latitude").points, cube.shape)
    if hemisphere.lower() in ("south", "s"):
        cube.data = np.ma.masked_where(lats > 0, cube.data)
    elif hemisphere.lower() in ("north", "n"):
        cube.data = np.ma.masked_where(lats < 0, cube.data)
    else:
        raise ValueError("Invalid hemisphere, must be 'north' or 'south'")
    return cube


def _set_cell_methods(cube, hemisphere):
    cube.cell_methods = ()
    cube.add_cell_method(iris.coords.CellMethod("point", coords="time"))
    cube.add_cell_method(
        iris.coords.CellMethod(
            "point",
            coords="latitude",
            comments=f"{hemisphere}ern hemisphere",
        )
    )
    cube.add_cell_method(iris.coords.CellMethod("point", coords="longitude"))
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


class Si3HemisPointMonthMeanTemporalmap(Temporalmap):
    """Si3HemisPointMonthMeanTemporalmap Processing Task"""

    _required_arguments = (
        "src",
        "dst",
        "hemisphere",
        "varname",
    )

    def __init__(self, arguments=None):
        Si3HemisPointMonthMeanTemporalmap.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        src = self.getarg("src", context)
        dst = self.getarg("dst", context)
        hemisphere = self.getarg("hemisphere", context)
        varname = self.getarg("varname", context)
        month = self.getarg("month", context, default=False)

        self.log_info(
            f"Temporal map for {varname} on {hemisphere}ern hemisphere at {dst}"
        )
        self.log_debug(f"Source file(s): {src}")

        if varname not in _meta_dict:
            self.log_warning(
                (
                    f"Invalid varname argument '{varname}', must be one of {_meta_dict.keys()}."
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
        this_leg = _mask_other_hemisphere(this_leg, hemisphere)
        if month:
            this_leg = _extract_month(this_leg, month)
            this_leg = _yearly_time_bounds(this_leg)

        if "convert_to" in _meta_dict[varname]:
            try:
                this_leg.convert_units(_meta_dict[varname]["convert_to"])
            except iris.exceptions.UnitConversionError:
                self.log_warning(
                    f"Cannot convert unit '{this_leg.units}' to '{_meta_dict[varname]['convert_to']}'"
                )

        long_name = (
            _meta_dict[varname]["long_name"]
            + " "
            + hemisphere
            + (f" {_month_name(month)}" if month else "")
        )
        comment = (
            f"{_meta_dict[varname]['long_name']} / **{varname}** in {hemisphere}ern hemisphere"
            + (f" in {_month_name(month)}" if month else "")
        )
        this_leg.long_name = long_name
        this_leg = helpers.cubes.set_metadata(
            this_leg,
            title=long_name,
            comment=comment,
            map_type="polar ice sheet",
        )

        this_leg = _set_cell_methods(this_leg, hemisphere)

        self.save(this_leg, dst)
