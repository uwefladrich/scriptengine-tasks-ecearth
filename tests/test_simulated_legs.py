"""Tests for scriptengine/tasks/ecearth/monitoring/simulated_legs.py"""

import os
from unittest.mock import patch

import yaml

from scriptengine.tasks.ecearth.monitoring.simulated_legs import SimulatedLegs

def test_simulated_legs_working(tmpdir):
    test_path = str(tmpdir)
    init = {
        'src': test_path,
        'dst': test_path + '/test.yml',
    }
    simulated_legs = SimulatedLegs(init)
    with patch.object(simulated_legs, 'save') as mock:
        simulated_legs.run(init)
    mock.assert_called_with(
        init['dst'],
        title="Simulated Legs",
        comment="Current amount of folders in output directory.",
        data=simulated_legs.count_leg_folders(init['src']),
        type=simulated_legs.diagnostic_type,
        )
    os.makedirs(test_path + '/output')
    simulated_legs = SimulatedLegs(init)
    with patch.object(simulated_legs, 'save') as mock:
        simulated_legs.run(init)
    mock.assert_called_with(
        init['dst'],
        title="Simulated Legs",
        comment="Current amount of folders in output directory.",
        data=simulated_legs.count_leg_folders(init['src']),
        type=simulated_legs.diagnostic_type,
        )

def test_simulated_legs_alternative(tmpdir):
    test_path = str(tmpdir)
    init = {
        'src': test_path,
        'dst': test_path + '/test.yml',
    }
    simulated_legs = SimulatedLegs(init)

    leg_info = {'config': {'schedule': {'leg': {'num': 5}}}}
    with open(test_path + '/leginfo.yml', 'w') as outfile:
        yaml.dump(leg_info, outfile, sort_keys=False)
    assert simulated_legs.get_leg_number(init['src']) == 5

    with open(test_path + '/leginfo.yml', 'w') as outfile:
        yaml.dump(init, outfile, sort_keys=False)
    assert simulated_legs.get_leg_number(init['src']) == -1
