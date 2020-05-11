from .foo import Foo

def task_loader_map():
    return {
        'foo': Foo,
        }
