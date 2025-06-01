import functools
from typing import Callable

__all__ = ['deferrable']


def deferrable(func: Callable):
    """Make the wrapped callable capable of having deferrable operation"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        deferrable_deferred_stack: list[Callable[[], None]] = []

        def run_deferred_ops():
            reversed_stack = reversed(deferrable_deferred_stack)
            for op in reversed_stack:
                op()
            # end for

        # end def

        try:
            # Execute the actual function.
            result = func(*args, **kwargs)
        except Exception as e:
            raise e  # Re-raise the error without modifying anything.
        finally:
            run_deferred_ops()
        # end try

        return result

    # end wrapper

    return wrapper
