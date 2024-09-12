"""
Useful decorators for the project
"""

from functools import wraps
from itertools import product

from typing import Callable, List


def run_for_each_arg(func: Callable):
    @wraps(func)
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


def check_for_list_of_inputs(check_for_true=True):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*arg_lists, **kwargs):
            # Generate all possible combinations of the arguments
            for combination in product(*arg_lists):
                if func(*combination, **kwargs) is check_for_true:
                    return check_for_true
            return not check_for_true

        return wrapper
    return decorator