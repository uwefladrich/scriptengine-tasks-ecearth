"""Tests for monitoring/simulatedyears_rte_scalar.py"""

from unittest.mock import patch

from monitoring.simulatedyears_rte_scalar import SimulatedyearsRteScalar


def test_simulatedyears_working(tmp_path):
    test_path = tmp_path / "test.yml"
    init = {"dst": test_path, "start": "1990-01-01", "end": "1995-01-01"}
    simulated_years = SimulatedyearsRteScalar(init)
    with patch.object(simulated_years, "save") as mock:
        simulated_years.run(init)
    mock.assert_called_with(
        init["dst"],
        title="Simulated Years",
        comment="Current number of simulated years.",
        value=5,
    )
