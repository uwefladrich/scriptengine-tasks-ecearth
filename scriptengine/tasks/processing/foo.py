"""Foo task for ScriptEngine."""

from scriptengine.tasks.base import Task


class Foo(Task):
    """Foo task, writes a (coloured) message to stdout
    """
    def __init__(self, parameters):
        super().__init__(__name__, parameters, required_parameters=["msg"])

    def run(self, context):
        self.log_info(self.msg)
        print(f"{self.msg}")