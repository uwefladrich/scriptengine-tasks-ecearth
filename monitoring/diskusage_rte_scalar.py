"""Processing Task that writes out the disk usage of a given folder."""
from pathlib import Path

from scriptengine.tasks.core import timed_runner

from .scalar import Scalar


def _dir_size(dir):
    if not dir.exists():
        raise FileNotFoundError
    if not dir.is_dir():
        raise NotADirectoryError
    return sum(f.stat().st_size for f in dir.glob("**/*") if f.is_file())


class DiskusageRteScalar(Scalar):
    """DiskusageRteScalar Processing Task"""

    _required_arguments = (
        "src",
        "dst",
    )

    def __init__(self, arguments=None):
        DiskusageRteScalar.check_arguments(arguments)
        super().__init__({**arguments, "title": None, "value": None})

    @timed_runner
    def run(self, context):
        src = Path(self.getarg("src", context))
        dst = Path(self.getarg("dst", context))
        self.log_info(f"Write disk usage of {src} to {dst}")

        try:
            value = _dir_size(src)
        except FileNotFoundError:
            self.log_warning(f"'{src}' does not exist")
            value = 0
        except NotADirectoryError:
            self.log_warning(f"'{src}' is not a directory")
            value = 0
        else:
            self.log_debug(f"Directory size: {value}")

        self.save(
            dst,
            title="Disk usage in GiB",
            comment=f"Current size of {src}",
            value=round(value / 2**30, 1),
        )
