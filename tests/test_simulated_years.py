"""Tests for scriptengine/tasks/ecearth/monitoring/simulated_years.py"""

from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.simulated_years import SimulatedYears

def test_simulated_years_working(tmpdir):
    test_path = str(tmpdir) + '/test.yml'
    init = {
        'dst': test_path,
        'start': "1990-01-01",
        'end': "1995-01-01"
    }
    simulated_years = SimulatedYears(init)
    with patch.object(simulated_years, 'save') as mock:
        simulated_years.run(init)
    mock.assert_called_with(
        init['dst'],
        title="Simulated Years",
        comment="Current number of simulated years.",
        data=5,
        type=simulated_years.diagnostic_type,
        )
