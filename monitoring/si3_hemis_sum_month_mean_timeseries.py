"""Processing Task that calculates the seasonal cycle of sea ice variables in one leg."""

import warnings
from pathlib import Path

import cf_units
import iris
from scriptengine.tasks.core import timed_runner

import helpers.cubes
import helpers.dates
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


def _set_cell_methods(cube, hemisphere):
    cube.cell_methods = (
        iris.coords.CellMethod("point", coords="time"),
        iris.coords.CellMethod(
            "sum", coords="area", intervals=f"{hemisphere}ern hemisphere"
        ),
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
        dst = Path(self.getarg("dst", context))
        varname = self.getarg("varname", context)
        hemisphere = self.getarg("hemisphere", context)
        month = self.getarg("month", context)
        domain = self.getarg("domain", context)

        self.log_info(f"Timeseries for {varname} ({hemisphere}ern hemisphere): {dst}")
        self.log_debug(f"Source file(s): {src}; domain file: {domain}")

        try:
            long_name = _meta_dict[varname]["long_name"]
        except KeyError:
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
        this_leg = helpers.cubes.extract_month(this_leg, month)
        this_leg = helpers.cubes.mask_other_hemisphere(this_leg, hemisphere)
        this_leg = helpers.cubes.annual_time_bounds(this_leg)

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
            f"{long_name} {helpers.dates.month_name(month)} {hemisphere}"
        )
        this_leg_summed.var_name = _meta_dict[varname]["var_name"] + hemisphere[0]

        metadata = {
            "comment": (
                f"Product of {long_name} / **{varname}** and grid-cell area, "
                f"summed over all grid cells of the {hemisphere}ern hemisphere."
            ),
            "title": f"{long_name} ({helpers.dates.month_name(month)} mean on the {hemisphere}ern hemisphere)",
        }
        this_leg_summed = helpers.cubes.set_metadata(this_leg_summed, **metadata)
        this_leg_summed = _set_cell_methods(this_leg_summed, hemisphere)
        self.save(this_leg_summed, dst)
