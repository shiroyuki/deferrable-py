from inspect import stack
from typing import Callable

__all__ = ['defer', 'NotDeferredError']


class NotDeferredError(RuntimeError):
    pass


def defer(op: Callable[[], None]):
    """ Defer the given operation to be executed at the end of the callable invocation,i.e., on the call exit. """
    call_stacks = stack()
    for call in call_stacks:
        if 'deferrable_deferred_stack' in call.frame.f_locals:
            call.frame.f_locals['deferrable_deferred_stack'].append(op)
            return
    raise NotDeferredError(op)