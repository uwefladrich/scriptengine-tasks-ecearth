"""Tests for scriptengine/tasks/ecearth/monitoring/nemo_time_mean_temporalmap.py"""

import pytest
import iris

from scriptengine.tasks.ecearth.monitoring.nemo_time_mean_temporalmap import NemoTimeMeanTemporalmap, NemoMonthMeanTemporalmap, NemoYearMeanTemporalmap

def test_nemo_time_mean_temporalmap_base(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoTimeMeanTemporalmap(init)
    with pytest.raises(NotImplementedError):
        ocean_time_map.run(init)

def test_nemo_year_mean_temporalmap_once(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoYearMeanTemporalmap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == 'global ocean'
    assert cube.attributes['diagnostic_type'] == 'temporal map'
    assert cube.data.shape[0] == 1

def test_nemo_year_mean_temporalmap_twice(tmpdir):
    init_a = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoYearMeanTemporalmap(init_a)
    ocean_time_map.run(init_a)
    init_b = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199009.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoYearMeanTemporalmap(init_b)
    ocean_time_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == 'global ocean'
    assert cube.attributes['diagnostic_type'] == 'temporal map'
    assert cube.data.shape[0] == 2


def test_nemo_month_mean_temporalmap_once(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoMonthMeanTemporalmap(init)
    ocean_time_map.run(init)
    cube = iris.load_cube(init['dst'])
    assert cube.attributes['map_type'] == 'global ocean'
    assert cube.attributes['diagnostic_type'] == 'temporal map'
    assert cube.data.shape[0] == len(init['src'])

def test_nemo_month_mean_temporalmap_twice(tmpdir):
    init_a = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199003.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoMonthMeanTemporalmap(init_a)
    ocean_time_map.run(init_a)
    init_b = {
        "src": ['./tests/testdata/NEMO_output_sivolu-199009.nc'],
        "dst": str(tmpdir) + '/test.nc',
        "varname": "sivolu",
    }
    ocean_time_map = NemoMonthMeanTemporalmap(init_b)
    ocean_time_map.run(init_b)
    cube = iris.load_cube(init_b['dst'])
    assert cube.attributes['map_type'] == 'global ocean'
    assert cube.attributes['diagnostic_type'] == 'temporal map'
    assert cube.data.shape[0] == len(init_a['src']) + len(init_b['src'])