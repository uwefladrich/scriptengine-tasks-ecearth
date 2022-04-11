"""Base class for temporal map processing tasks."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import iris
import iris.cube
from scriptengine.exceptions import (
    ScriptEngineTaskArgumentInvalidError,
    ScriptEngineTaskRunError,
)
from scriptengine.tasks.core import Task


class Temporalmap(Task):
    """Temporalmap Processing Task"""

    def save(self, new_cube: iris.cube.Cube, dst: Path):
        """save temporal map cube in netCDF file"""
        self.log_debug(f"Saving temporal map cube to {dst}")
        new_cube.attributes["diagnostic_type"] = "temporal map"
        try:
            current_cube = iris.load_cube(str(dst))
        except OSError:  # file does not exist yet.
            iris.save(new_cube, dst)
            return

        current_bounds = current_cube.coord("time").bounds
        new_bounds = new_cube.coord("time").bounds
        if current_bounds[-1][-1] > new_bounds[0][0]:
            msg = "Non-monotonic coordinate. Cube will not be saved."
            self.log_error(msg)
            raise ScriptEngineTaskRunError()

        # Iris changes metadata when saving/loading cube
        # save & reload to prevent metadata mismatch
        # keep tempfile until the merged cube is saved
        with NamedTemporaryFile() as tf:
            iris.save(new_cube, tf.name, saver="nc")
            new_cube = iris.load_cube(tf.name)
            new_cube.attributes = current_cube.attributes

            cube_list = iris.cube.CubeList([current_cube, new_cube])
            merged_cube = cube_list.concatenate_cube()

            dst_copy = dst.with_name(f"{dst.stem}_copy{dst.suffix}")
            iris.save(merged_cube, str(dst_copy))

        dst.unlink()
        dst_copy.rename(dst)

    def check_file_extension(self, dst: Path):
        """check if destination file has a valid netCDF extension"""
        if dst.suffix != ".nc":
            self.log_error(f"Invalid netCDF extension in dst '{dst}'")
            raise ScriptEngineTaskArgumentInvalidError()
