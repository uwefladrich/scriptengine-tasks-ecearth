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
        
        # The rollback function in EC-Earth will reset the initial time
        # for OpenIFS each restart.
        # If we start in 1990-01-01, the time coordinate for 1st and 2nd
        # leg will be 1990-01-01 but it will be 1991-01-01 for 3rd leg
        # and 1992-01-01 for 4th leg etc.
        # Iris will not be able to merge the cubes.
        # Here we convert the time coordinate in new_cube, e.g.
        # seconds since 1992-01-01 00:00:00
        # to the time coordinate of the current_cube e.g.
        # seconds since 1990-01-01 00:00:00
        new_cube.coord("time").convert_units(current_cube.coord("time").units)
        # We also need to match the attribute time_origin between
        # new_cube and current_cube to make Iris happy.
        if (     "time_origin" in current_cube.coord("time").attributes.keys()
             and "time_origin" in     new_cube.coord("time").attributes.keys() ):
            new_cube.coord("time").attributes["time_origin"] = current_cube.coord("time").attributes["time_origin"]
        
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
