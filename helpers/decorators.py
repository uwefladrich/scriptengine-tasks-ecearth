"""Helper module containing helpful decorators."""

from functools import wraps
from time import time

def timing(func):
    @wraps(func)
    def wrap(*args, **kw):
        t_start = time()
        result = func(*args, **kw)
        t_end = time()
        print(f"function:{func.__name__} took: {t_end-t_start} sec")
        return result
    return wrap
