"""Processing Task that writes out the disk usage of a given folder."""
import os

from scriptengine.tasks.base.timing import timed_runner
from .scalar import Scalar

class DiskusageRteScalar(Scalar):
    """DiskusageRteScalar Processing Task"""
    def __init__(self, parameters):
        super().__init__(
            parameters={**parameters, 'value': None, 'title': None},
            required_parameters=['src']
            )

    @timed_runner
    def run(self, context):
        src = self.getarg('src', context)
        dst = self.getarg('dst', context)
        self.log_info(f"Write disk usage of {src} to {dst}")

        self.value = round(self.get_directory_size(src) * 1e-9, 1)
        self.title = "Disk Usage in GB"
        self.log_debug(f"Size of Directory: {self.value}")

        self.save(
            dst,
            title=self.title,
            comment=f"Current size of {src}.",
            value=self.value,
        )

    def get_directory_size(self, path):
        """Returns the size of `path` in Bytes."""
        self.log_debug("Getting directory size.")
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_directory_size(entry.path)
        except (NotADirectoryError, FileNotFoundError):
            self.log_warning(f"{path} is not a directory. Returning -1.")
            return -1e9 # gets multiplied with 1e-9 again
        except PermissionError:
            self.log_warning(f"No permission to open {path}. Returning -1.")
            return -1e9 # gets multiplied with 1e-9 again

        return total
