"""
Useful decorators for the project
"""

from typing import Callable, List


def run_for_each_arg(func: Callable):
    def wrapper(*args, **kwargs) -> List:
        results = []
        for arg in args:
            result = func(arg, **kwargs)
            results.append(result)
        return results

    return wrapper
