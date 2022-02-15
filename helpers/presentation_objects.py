"""
Initialize presentation objects for visualization
"""

from pathlib import Path

import cftime
import imageio
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import yaml

import helpers.exceptions as exceptions
import helpers.map_type_handling as type_handling
from helpers.file_handling import ChangeDirectory


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
            loaded_cube = iris.load_cube(str(path))
        except OSError:
            raise exceptions.PresentationException(f"File not found! Ignoring {path}")
        if loaded_cube.attributes["diagnostic_type"] == "time series":
            return TimeseriesLoader(path, loaded_cube)
        if loaded_cube.attributes["diagnostic_type"] == "map":
            return MapLoader(path, loaded_cube)
        if loaded_cube.attributes["diagnostic_type"] == "temporal map":
            return TemporalmapLoader(path, loaded_cube)
        raise exceptions.PresentationException(
            f"Invalid diagnostic type {loaded_cube.attributes['diagnostic_type']}"
        )
    raise exceptions.PresentationException(f"Invalid file extension of {path}")


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
            raise exceptions.PresentationException(
                f"File not found! Ignoring {self.path}"
            )


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
        ax.plot(coord_points, self.cube.data, marker="o")
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
        ax.set_xlabel(format_title(x_coord.name()))
        ax.set_ylabel(format_title(self.cube.long_name, self.cube.units))

        plt.tight_layout()
        with ChangeDirectory(dst_folder):
            fig.savefig(dst_file, bbox_inches="tight")
            plt.close(fig)

        image_dict = {
            "title": self.cube.attributes["title"],
            "path": dst_file,
            "comment": self.cube.attributes["comment"],
        }
        return image_dict

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
        map_handler = type_handling.function_mapper(map_type)
        if map_handler is None:
            raise exceptions.InvalidMapTypeException(map_type)

        unit_text = f"{format_units(self.cube.units)}"
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

        image_dict = {
            "title": self.cube.attributes["title"],
            "path": dst_file,
            "comment": self.cube.attributes["comment"],
        }
        return image_dict


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
        map_handler = type_handling.function_mapper(map_type)
        if map_handler is None:
            raise exceptions.InvalidMapTypeException(map_type)

        png_dir = self.path.stem + "_frames"
        with ChangeDirectory(dst_folder):
            png_dir.mkdir(exist_ok=True)
            number_of_pngs = len(png_dir.iterdir())

        unit_text = f"{format_units(self.cube.units)}"
        dst_file = f"./{self.path.stem}.gif"
        number_of_time_steps = len(self.cube.coord("time").points)
        with ChangeDirectory(f"{dst_folder}/{png_dir}"):
            for time_step in range(number_of_pngs, number_of_time_steps):
                time_coord = self.cube.coord("time")
                time_bounds = time_coord.bounds[time_step]
                dates = cftime.num2pydate(time_bounds, time_coord.units.name)
                date_title = f"{dates[0].strftime('%Y')}"
                plot_title = format_title(self.cube.long_name)
                fig = map_handler(
                    self.cube[time_step],
                    title=plot_title,
                    dates=date_title,
                    units=unit_text,
                    **kwargs,
                )
                fig.savefig(
                    f"./{self.path.stem}-{time_step:03}.png", bbox_inches="tight"
                )
                plt.close(fig)
            images = []
            for file_name in sorted(Path().iterdir()):
                images.append(imageio.imread(file_name))
            imageio.mimsave(f".{dst_file}", images, fps=2)

        image_dict = {
            "title": self.cube.attributes["title"],
            "path": dst_file,
            "comment": self.cube.attributes["comment"],
        }
        return image_dict


def format_title(name, units=None):
    """
    Create Plot/Axis Title from Iris cube/coordinate

    Slight variance on _title() in iris/quickplot.py.
    """
    title = name.replace("_", " ").title()
    unit_text = format_units(units)
    if unit_text and unit_text != "1":
        title += " / {}".format(unit_text)
    return title


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
