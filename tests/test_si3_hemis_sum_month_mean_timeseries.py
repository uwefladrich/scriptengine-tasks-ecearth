"""Tests for scriptengine/tasks/ecearth/monitoring/si3_hemis_sum_month_mean_timeseries.py"""

from unittest.mock import patch

import iris

from scriptengine.tasks.ecearth.monitoring.si3_hemis_sum_month_mean_timeseries import Si3HemisSumMonthMeanTimeseries, meta_dict

def test_si3_hemis_sum_month_mean_timeseries_working(tmpdir):
    init = {
        "src": [
            './tests/testdata/NEMO_output_sivolu-199003.nc',
            './tests/testdata/NEMO_output_sivolu-199009.nc',
            ],
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
        "hemisphere": "north",
    }
    ice_time_series = Si3HemisSumMonthMeanTimeseries(init)
    ice_time_series.run(init)
    cube = iris.load_cube(str(tmpdir) + '/test.nc')
    assert cube.name() == 'sea_ice_volume'
    assert cube.attributes['title'] is not None
    assert cube.attributes['comment'] is not None
    assert cube.attributes['diagnostic_type'] == 'time series'
    assert cube.cell_methods == (
        iris.coords.CellMethod('point', coords='time'),
        iris.coords.CellMethod('sum', coords='area', intervals='northern hemisphere'),
        )

def test_si3_hemis_sum_month_mean_timeseries_wrong_varname(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "tos",
        "hemisphere": "south",
    }
    ice_time_series = Si3HemisSumMonthMeanTimeseries(init)
    ice_time_series.run(init)
    with patch.object(ice_time_series, 'log_warning') as mock:
        ice_time_series.run(init)
    mock.assert_called_with((
                f"'varname' must be one of the following: {meta_dict.keys()} "
                f"Diagnostic will not be treated, returning now."))

def test_si3_hemis_sum_month_mean_timeseries_wrong_hemisphere(tmpdir):
    init = {
        "src": './tests/testdata/NEMO_output_sivolu-199003.nc',
        "dst": str(tmpdir) + '/test.nc',
        "domain": './tests/testdata/domain_cfg_example.nc',
        "varname": "sivolu",
        "hemisphere": "east",
    }
    ice_time_series = Si3HemisSumMonthMeanTimeseries(init)
    ice_time_series.run(init)
    with patch.object(ice_time_series, 'log_warning') as mock:
        ice_time_series.run(init)
    mock.assert_called_with((
                f"'hemisphere' must be 'north' or 'south' but is '{init['hemisphere']}'."
                f"Diagnostic will not be treated, returning now."))
