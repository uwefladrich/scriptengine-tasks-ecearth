"""Tests for scriptengine/tasks/ecearth/monitoring/map.py"""

import os
import datetime

import pytest
import iris
from unittest.mock import patch

from scriptengine.tasks.ecearth.monitoring.map import Map

def test_dynamic_map_dst_error():
    test_map = Map({})
    assert test_map.correct_file_extension("test.yml") == False
