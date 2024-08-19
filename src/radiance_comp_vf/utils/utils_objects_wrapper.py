"""
Wrapper for objects and methods.
"""



def object_method_wrapper(obj, method_name: str, *args, **kwargs):
    """
    Wrapper function to call a method on an object, useful to call methods in a parallelized environment.
    :param obj: The object whose method will be called.
    :param method_name: The name of the method to call.
    :param args: Arguments to pass to the method.
    :param kwargs: Keyword arguments to pass to the method.
    :return: The result of the method call.
    """
    method = getattr(obj, method_name)
    return method(*args, **kwargs)