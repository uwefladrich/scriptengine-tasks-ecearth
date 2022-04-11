"""Base class for map processing tasks."""
from pathlib import Path
from tempfile import NamedTemporaryFile

import iris
import iris.cube
from scriptengine.exceptions import (
    ScriptEngineTaskArgumentInvalidError,
    ScriptEngineTaskRunError,
)
from scriptengine.tasks.core import Task

import helpers.cubes


class Map(Task):
    """Map Processing Task"""

    def save(self, new_cube: iris.cube.Cube, dst: Path):
        """save map cube in netCDF file"""
        self.log_debug(f"Saving map cube to '{dst}'")
        new_cube.attributes["diagnostic_type"] = "map"
        try:
            current_cube = iris.load_cube(str(dst))
        except OSError:  # file does not exist yet.
            iris.save(new_cube, str(dst))
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

            current_cube.cell_methods = new_cube.cell_methods
            cube_list = iris.cube.CubeList([current_cube, new_cube])
            merged_cube = cube_list.merge_cube()
            simulation_avg = self.compute_simulation_avg(merged_cube)

            dst_copy = dst.with_name(f"{dst.stem}_copy{dst.suffix}")
            iris.save(simulation_avg, str(dst_copy))

        dst.unlink()
        dst_copy.rename(dst)

    def check_file_extension(self, dst: Path):
        """check if destination file has a valid netCDF extension"""
        if dst.suffix != ".nc":
            self.log_error(f"Invalid netCDF extension in dst '{dst}'")
            raise ScriptEngineTaskArgumentInvalidError()

    def compute_simulation_avg(self, merged_cube):
        """
        Compute Time Average for the whole simulation.
        """
        self.log_debug("Computing simulation average.")
        time_weights = helpers.cubes.compute_time_weights(
            merged_cube, merged_cube.shape
        )
        simulation_avg = merged_cube.collapsed(
            "time",
            iris.analysis.MEAN,
            weights=time_weights,
        )
        return simulation_avg
