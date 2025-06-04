import functools
from inspect import iscoroutinefunction
from typing import Callable, Awaitable

__all__ = ['deferrable']


def deferrable(func: Callable):
    """Make the wrapped callable capable of having deferred operations"""

    if iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            deferrable_deferred_stack: list[Callable[[], Awaitable[None]]] = []

            async def run_deferred_ops():
                reversed_stack = reversed(deferrable_deferred_stack)
                for op in reversed_stack:
                    if iscoroutinefunction(op):
                        await op()
                    else:
                        op()
                # end for

            # end def

            try:
                # Execute the actual function.
                result = await func(*args, **kwargs)
            except Exception as e:
                raise e  # Re-raise the error without modifying anything.
            finally:
                await run_deferred_ops()
            # end try

            return result
        # end wrapper
    else:
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
    # end if

    return wrapper

