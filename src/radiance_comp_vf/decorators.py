"""
Useful decorators for the project
"""

from functools import wraps
from itertools import product

from typing import Callable, List


def run_for_each_arg(func: Callable):
    def wrapper(*args, **kwargs) -> List:
        results = []
        for arg in args:
            result = func(arg, **kwargs)
            results.append(result)
        return results

    return wrapper





def check_for_list_of_inputs(func: Callable):
    @wraps(func)
    def wrapper(*arg_lists, **kwargs):
        # Generate all possible combinations of the arguments
        for combination in product(*arg_lists):
            if func(*combination, **kwargs):
                return True
        return False

    return wrapper
