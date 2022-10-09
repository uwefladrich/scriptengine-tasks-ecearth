"""
Initialize presentation objects for visualization
"""

from pathlib import Path
from textwrap import wrap

import cftime
import imageio.v3 as imageio
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import yaml

from helpers.exceptions import InvalidMapTypeException, PresentationException
from helpers.files import ChangeDirectory
from helpers.map_type_handling import function_mapper


class PresentationObject:
    def __init__(self, dst_folder, path, **kwargs):
        self.dst_folder = Path(dst_folder)
        self.path = Path(path)
        self.custom_input = kwargs
        self.loader = get_loader(self.path)

    def create_dict(self):
        loaded_dict = self.loader.load(self.dst_folder, **self.custom_input)
        return {"presentation_type": self.loader.pres_type, **loaded_dict}


def get_loader(path):
    if path.suffix in (".yml", ".yaml"):
        return ScalarLoader(path)
    if path.suffix == ".nc":
        try:
            # Iris before 3.3 can't handle pathlib's Path, needs string
            cube = iris.load_cube(str(path))
        except OSError:
            raise PresentationException(f"File not found: {path}")
        loader_map = {
            "time series": TimeseriesLoader,
            "map": MapLoader,
            "temporal map": TemporalmapLoader,
        }
        diag_type = cube.attributes["diagnostic_type"]
        try:
            return loader_map[diag_type](path, cube)
        except KeyError:
            raise PresentationException(f"Invalid diagnostic type: {diag_type}")
    raise PresentationException(f"Invalid file extension: {path}")


class PresentationObjectLoader:
    def __init__(self, path):
        self.path = Path(path)
        self.diag_type = "invalid"
        self.pres_type = "invalid"

    def load(self, **kwargs):
        raise NotImplementedError


class ScalarLoader(PresentationObjectLoader):
    def __init__(self, path):
        self.path = Path(path)
        self.diag_type = "scalar"
        self.pres_type = "text"

    def load(self, *args, **kwargs):
        try:
            with open(self.path) as yml_file:
                loaded_dict = yaml.load(yml_file, Loader=yaml.FullLoader)
            return loaded_dict
        except FileNotFoundError:
            raise PresentationException(f"File not found: {self.path}")


class TimeseriesLoader(PresentationObjectLoader):
    def __init__(self, path, cube):
        self.path = Path(path)
        self.cube = cube
        self.diag_type = "time series"
        self.pres_type = "image"

    def load(self, dst_folder, **kwargs):
        """
        Load time series diagnostic and call plot creator.
        """
        dst_file = f"./{self.path.stem}.png"

        x_coord = self.cube.coords()[0]
        if "second since" in x_coord.units.name or "hour since" in x_coord.units.name:
            dates = cftime.num2pydate(x_coord.points, x_coord.units.name)
            coord_points = format_dates(dates)
        else:
            coord_points = x_coord.points

        fig = plt.figure(figsize=(6, 4), dpi=150)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(coord_points, self.cube.data, color="k")
        plt.setp(ax.spines.values(), color="grey")
        ax.grid()
        if "second since" in x_coord.units.name or "hour since" in x_coord.units.name:
            fig.autofmt_xdate()

        minor_step, major_step = self._determine_intervals(len(coord_points))
        ax.set_xticks(coord_points[minor_step - 1 :: major_step])
        ax.set_xticks(coord_points[minor_step - 1 :: minor_step], minor=True)
        ax.set_xticklabels(coord_points[minor_step - 1 :: major_step])

        ax.ticklabel_format(
            axis="y", style="sci", scilimits=(-3, 6), useOffset=False, useMathText=True
        )
        ax.set_ylim(kwargs.get("value_range", [None, None]))

        ax.set_title(format_title(self.cube.long_name))
        ax.set_xlabel(format_label(x_coord.name()))
        ax.set_ylabel(format_label(self.cube.long_name, self.cube.units))

        plt.tight_layout()
        with ChangeDirectory(dst_folder):
            fig.savefig(dst_file, bbox_inches="tight")
            plt.close(fig)

        return {
            "title": self.cube.attributes["title"],
            "path": dst_file,
            "comment": self.cube.attributes["comment"],
        }

    def _determine_intervals(self, coord_length):
        """
        compute the minor and major ticking intervals based on # of data points.
        """
        if coord_length < 10:
            return 1, 1
        elif coord_length < 20:
            return 2, 2
        elif coord_length < 50:
            return 5, 5
        elif coord_length < 100:
            return 5, 10
        else:
            return 10, 20


class MapLoader(PresentationObjectLoader):
    def __init__(self, path, cube):
        self.path = Path(path)
        self.cube = cube
        self.diag_type = "map"
        self.pres_type = "image"

    def load(self, dst_folder, **kwargs):
        """
        Load map diagnostic and determine map type.
        """
        map_type = self.cube.attributes["map_type"]
        map_handler = function_mapper(map_type)
        if map_handler is None:
            raise InvalidMapTypeException(map_type)

        unit_text = format_units(self.cube.units)
        time_coord = self.cube.coord("time")
        time_bounds = time_coord.bounds[0]
        dates = cftime.num2pydate(time_bounds, time_coord.units.name)
        plot_title = format_title(self.cube.long_name)
        date_title = f"{dates[0].strftime('%Y')} - {dates[-1].strftime('%Y')}"
        fig = map_handler(
            self.cube,
            title=plot_title,
            dates=date_title,
            units=unit_text,
            **kwargs,
        )
        dst_file = f"./{self.path.stem}.png"
        with ChangeDirectory(dst_folder):
            fig.savefig(dst_file, bbox_inches="tight")
            plt.close(fig)

        return {
            "title": self.cube.attributes["title"],
            "path": dst_file,
            "comment": self.cube.attributes["comment"],
        }


class TemporalmapLoader(PresentationObjectLoader):
    def __init__(self, path, cube):
        self.path = Path(path)
        self.cube = cube
        self.diag_type = "temporal map"
        self.pres_type = "image"

    def load(self, dst_folder, **kwargs):
        """
        Load map diagnostic and determine map type.
        """
        map_type = self.cube.attributes["map_type"]
        map_handler = function_mapper(map_type)
        if map_handler is None:
            raise InvalidMapTypeException(map_type)

        png_dir = dst_folder / Path(self.path.stem + "_frames")
        png_dir.mkdir(exist_ok=True)
        num_existing_pngs = len(list(png_dir.iterdir()))

        gif_file = self.path.with_suffix(".gif").name

        time = self.cube.coord("time")
        dates = [cftime.num2pydate(t, time.units.name) for t in time.points]
        num_months = len(set(d.month for d in dates))

        for ts in range(num_existing_pngs, len(dates)):
            fig = map_handler(
                self.cube[ts],
                title=format_title(self.cube.long_name),
                dates=dates[ts].strftime("%B %Y" if num_months > 1 else "%Y"),
                units=format_units(self.cube.units),
                **kwargs,
            )
            fig.savefig(png_dir / f"{self.path.stem}-{ts:03}.png", bbox_inches="tight")
            plt.close(fig)

        frames = [imageio.imread(png) for png in sorted(png_dir.iterdir())]
        imageio.imwrite(dst_folder / gif_file, frames, duration=500, loop=0)

        return {
            "title": self.cube.attributes["title"],
            "comment": self.cube.attributes["comment"],
            "path": "./" + gif_file,
        }


def format_title(name):
    """
    String formatting for plot titles

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ")
    # create multiline string if it becomes too long
    # cf. https://stackoverflow.com/a/10634897
    title = "\n".join(wrap(title, 40))
    return title


def format_label(name, units=None):
    """
    String formatting for axis labels

    Slight variance on _title() in iris/quickplot.py.
    """
    label = name.replace("_", " ")
    unit_text = format_units(units)
    if unit_text and unit_text != "1":
        label += " / {}".format(unit_text)
    # create multiline string if it becomes too long
    # cf. https://stackoverflow.com/a/10634897
    label = "\n".join(wrap(label, 40))
    return label


def format_units(units):
    """Format Cube Units as String"""
    if not (units is None or units.is_unknown() or units.is_no_unit()):
        if qplt._use_symbol(units):
            return units.symbol
        else:
            return units
    else:
        return None


def format_dates(dates):
    fmt_dates = []
    for date in dates:
        fmt_dates.append(date.year)
    if len(set(fmt_dates)) != len(fmt_dates):
        fmt_dates = []
        for date in dates:
            fmt_dates.append(date.strftime("%Y-%m"))
    return fmt_dates
