import iris
import pytest
import yaml
from iris.cube import Cube
from scriptengine.exceptions import (
    ScriptEngineTaskArgumentInvalidError,
    ScriptEngineTaskArgumentMissingError,
)
from scriptengine.yaml.parser import parse

from monitoring.linear_combination import LinearCombination


def _from_yaml(string):
    return parse(yaml.load(string, Loader=yaml.FullLoader))


@pytest.fixture
def create_test_cube(tmp_path):
    def _test_cube(varname, value):
        cube = Cube([value], var_name=varname, units="1")
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


def test_create_src_no_list():
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: foo
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})


def test_create_src_items_no_dict():
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: [foo]
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})


def test_create_src_items_missing_keys():
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: [{foo: bar}]
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentMissingError):
        t.run({})


def test_create_src_invalid_factor():
    t = _from_yaml(
        """
        ece.mon.linear_combination:
          src: [{path: foo, varname: bar, factor: baz}]
          dst: bar
        """
    )
    with pytest.raises(ScriptEngineTaskArgumentInvalidError):
        t.run({})


def test_create_dst_no_dict(create_test_cube):
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


def test_create_dst_missing_key(create_test_cube):
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
