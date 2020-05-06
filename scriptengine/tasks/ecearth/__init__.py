""" ScriptEngine EC-Earth tasks

This module provides SE tasks for the EC-Earth ESM
"""

from .slurm import Sbatch


def task_loader_map():
    return {'sbatch': Sbatch}
