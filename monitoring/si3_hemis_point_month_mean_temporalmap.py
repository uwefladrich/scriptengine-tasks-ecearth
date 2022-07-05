"""Processing Task that creates a 2D time map of sea ice concentration."""

from pathlib import Path

import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes
import helpers.dates

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


def _set_cell_methods(cube, hemisphere):
    cube.cell_methods = (
        iris.coords.CellMethod("point", coords="time"),
        iris.coords.CellMethod(
            "point",
            coords="latitude",
            comments=f"{hemisphere}ern hemisphere",
        ),
        iris.coords.CellMethod("point", coords="longitude"),
    )
    return cube


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
        dst = Path(self.getarg("dst", context))
        hemisphere = self.getarg("hemisphere", context)
        varname = self.getarg("varname", context)
        month = self.getarg("month", context, default=False)

        self.log_info(f"Temporalmap for {varname} ({hemisphere}ern hemisphere): {dst}")
        self.log_debug(f"Source file(s): {src}")

        if varname not in _meta_dict:
            self.log_warning(
                (
                    f"Invalid varname '{varname}', must be one of {_meta_dict.keys()}; "
                    "diagnostic will not be ignored."
                )
            )
            return
        if hemisphere not in ("north", "south"):
            self.log_warning(
                (
                    f"Invalid hemisphere '{hemisphere}', must be 'north' or 'south'; "
                    "diagnostic will not be ignored."
                )
            )
            return
        self.check_file_extension(dst)

        this_leg = helpers.cubes.load_input_cube(src, varname)
        this_leg = helpers.cubes.remove_aux_time(this_leg)
        this_leg = helpers.cubes.mask_other_hemisphere(this_leg, hemisphere)
        if month:
            this_leg = helpers.cubes.extract_month(this_leg, month)
            this_leg = helpers.cubes.annual_time_bounds(this_leg)

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
            + (f" {helpers.dates.month_name(month)}" if month else "")
        )
        comment = (
            f"{_meta_dict[varname]['long_name']} / **{varname}** in {hemisphere}ern hemisphere"
            + (f" in {helpers.dates.month_name(month)}" if month else "")
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
