"""Processing Task that writes out the disk usage of a given folder."""
import os

from .write_scalar import WriteScalar
from scriptengine.tasks.base.timing import timed_runner

class DiskUsage(WriteScalar):
    """DiskUsage Processing Task"""
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.title = "Disk Usage in GB"
        self.comment = f"Current size of {self.dst}."
        self.type = "scalar"

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        self.log_info(f"Write disk usage to {dst}")

        value = round(self.get_directory_size(src) * 1e-9, 1)

        self.save(
            dst,
            title=self.title,
            comment=self.comment,
            data=value,
            type=self.type,
        )

    def get_directory_size(self, path):
        """Returns the size of `path` in Bytes."""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_directory_size(entry.path)
        except NotADirectoryError:
            self.log_warning(f"{path} is not a directory. Returning -1.")
            return -1
        except PermissionError:
            self.log_warning(f"No permission to open {path}. Returning -1.")
            return -1

        return total
