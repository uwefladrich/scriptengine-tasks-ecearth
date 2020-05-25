"""Processing Task that writes out the disk usage of a given folder."""
from .write_scalar import WriteScalar
import os
from scriptengine.jinja import render as j2render

class DiskUsage(WriteScalar):
    def __init__(self, parameters):
        required = [
            "src",
            "dst",
        ]
        super(WriteScalar, self).__init__(__name__, parameters, required_parameters=required)
        self.long_name = "Disk Usage in GB"
        self.comment = "Current size of output directory."
        self.type = "scalar"
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.src},{self.dst})"
        )

    def run(self, context):
        src = j2render(self.src, context)
        dst = j2render(self.dst, context)

        value = round(self.get_directory_size(src) * 1e-9, 3)

        self.save(
            dst,
            long_name=self.long_name,
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

