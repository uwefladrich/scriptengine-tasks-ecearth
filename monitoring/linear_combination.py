from operator import itemgetter

import iris
from scriptengine.exceptions import (
    ScriptEngineTaskArgumentInvalidError,
    ScriptEngineTaskArgumentMissingError,
    ScriptEngineTaskRunError,
)
from scriptengine.tasks.core import Task, timed_runner

import helpers.cubes


class LinearCombination(Task):

    _required_arguments = (
        "src",
        "dst",
    )

    def __init__(self, arguments):
        LinearCombination.check_arguments(arguments)
        super().__init__(arguments)

    @timed_runner
    def run(self, context):
        self.log_info("Create new netCDF file from linear combination of inputs")

        sources = self.getarg("src", context)
        if not isinstance(sources, list):
            self.log_error("Invalid 'src' argument, must be a list")
            raise ScriptEngineTaskArgumentInvalidError

        result = 0  # Initialize sum of scaled cubes
        for src in sources:
            self.log_debug(f"Processing source {src}")
            try:
                path, varname = itemgetter("path", "varname")(src)
            except TypeError:
                self.log_error("The list items of the 'src' argument must be dicts")
                raise ScriptEngineTaskArgumentInvalidError
            except KeyError as e:
                self.log_error(f"Missing key(s) {e} in 'src' list item")
                raise ScriptEngineTaskArgumentMissingError

            try:
                factor = float(src.get("factor", 1.0))
            except (ValueError, TypeError) as e:
                self.log_error(
                    f"Unable to convert the 'factor' argument to a number: {e}"
                )
                raise ScriptEngineTaskArgumentInvalidError

            summand = helpers.cubes.load_input_cube(path, varname)
            summand = helpers.cubes.remove_aux_time(summand)

            scaled_summand = factor * summand
            # Multiplying an Iris cube with a scalar will sometimes "simplify"
            # units, whereas we want to retain the original units of the summand
            scaled_summand.convert_units(summand.units)

            try:
                result += scaled_summand
            except Exception as e:
                self.log_error(f"Error adding '{summand.name()}': {e}")
                raise ScriptEngineTaskRunError

        self.log_debug("All sources processed")

        dst = self.getarg("dst", context)
        try:
            path, varname = itemgetter("path", "varname")(dst)
        except TypeError:
            self.log_error(f"The 'dst' argument must be a dict")
            raise ScriptEngineTaskArgumentInvalidError
        except KeyError as e:
            self.log_error(f"Missing key(s) {e} in 'src' argument")
            raise ScriptEngineTaskArgumentMissingError

        result.var_name = varname
        if dst.get("longname", False):
            result.long_name = dst["longname"]
        if dst.get("standardname", False):
            try:
                result.standard_name = dst["standardname"]
            except ValueError as e:
                self.log_warning(f"Standard name could not be set: {e}")
        if dst.get("unit", False):
            try:
                result.convert_units(dst["unit"])
            except ValueError as e:
                self.log_error(f"Unit conversion error: {e}")
                raise ScriptEngineTaskArgumentInvalidError

        self.log_debug(f"Saving result to {path}")
        iris.save(result, path, saver="nc")
