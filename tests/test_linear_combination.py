import iris
import pytest
import yaml
from iris.cube import Cube
from scriptengine.exceptions import (
    ScriptEngineTaskArgumentInvalidError,
    ScriptEngineTaskArgumentMissingError,
    ScriptEngineTaskRunError,
)
from scriptengine.yaml.parser import parse

from monitoring.linear_combination import LinearCombination


def _from_yaml(string):
    return parse(yaml.load(string, Loader=yaml.FullLoader))


@pytest.fixture
def create_test_cube(tmp_path):
    def _test_cube(varname, value, units="1"):
        cube = Cube([value], var_name=varname, units=units)
        fpath = tmp_path / f"{varname.lower()}.nc"
        iris.save(cube, fpath)
        return fpath

    return _test_cube


def test_create():
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: foo
          dst: bar
        """
    )
    assert type(t) == LinearCombination


def test_create_src_no_list(caplog):
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: foo
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})
    assert "Invalid 'src' argument, must be a list" in caplog.text


def test_create_src_items_no_dict(caplog):
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: [foo]
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})
    assert "The list items of the 'src' argument must be dicts" in caplog.text


def test_create_src_items_missing_keys(caplog):
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: [{foo: bar}]
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentMissingError):
        t.run({})
    assert "Missing key(s) " in caplog.text


def test_create_src_invalid_factor(caplog):
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: [{path: foo, varname: bar, factor: baz}]
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})
    assert "Unable to convert the 'factor' argument to a number" in caplog.text


def test_create_dst_no_dict(caplog, create_test_cube):
    c1 = create_test_cube("C1", 1.0)
    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              path: {c1}
              varname: C1
          dst: foo
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})
    assert "The 'dst' argument must be a dict" in caplog.text


def test_create_dst_missing_key(caplog, create_test_cube):
    c1 = create_test_cube("C1", 1.0)
    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              path: {c1}
              varname: C1
          dst:
            path: foo
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentMissingError):
        t.run({})
    assert "Missing key(s) " in caplog.text


def test_add_cubes(tmp_path, create_test_cube):
    c1 = create_test_cube("C1", 1.0)
    c2 = create_test_cube("C2", 2.0)
    c3 = tmp_path / "c3.nc"

    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              varname: C1
              path: {c1}
            -
              varname: C2
              path: {c2}
          dst:
            varname: C3
            longname: Air temperature
            standardname: temperature
            path: {c3}
        """
    )
    t.run({})


def test_incompatible_units(tmp_path, caplog, create_test_cube):
    c1 = create_test_cube("C1", 1.0, "m")
    c2 = create_test_cube("C2", 2.0, "kg")
    c3 = tmp_path / "c3.nc"

    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              varname: C1
              path: {c1}
            -
              varname: C2
              path: {c2}
          dst:
            varname: C3
            longname: Air temperature
            standardname: temperature
            path: {c3}
        """
    )
    with pytest.raises(ScriptEngineTaskRunError):
        t.run({})
    assert "Error adding " in caplog.text


def test_convert_unit(create_test_cube, tmp_path):
    c1 = create_test_cube("C1", 1000.0, "m")
    c2 = tmp_path / "c2.nc"

    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              varname: C1
              path: {c1}
          dst:
            varname: C2
            path: {c2}
            unit: km
        """
    )
    t.run({})
    result = iris.load_cube(str(c2))
    assert result.units == "km"
    assert result.data == [1.0]


def test_convert_invalid_unit(create_test_cube, tmp_path, caplog):
    c1 = create_test_cube("C1", 1000.0, "m")
    c2 = tmp_path / "c2.nc"

    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              varname: C1
              path: {c1}
          dst:
            varname: C2
            path: {c2}
            unit: foo
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})
    assert "Unit conversion error: " in caplog.text


def test_convert_incompatible_unit(create_test_cube, tmp_path, caplog):
    c1 = create_test_cube("C1", 1000.0, "m")
    c2 = tmp_path / "c2.nc"

    t = _from_yaml(
        f"""
        ece.mon.linear_combination:
          src:
            -
              varname: C1
              path: {c1}
          dst:
            varname: C2
            path: {c2}
            unit: kg
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})
    assert "Unit conversion error: " in caplog.text
