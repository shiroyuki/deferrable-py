from inspect import stack
from typing import Callable

__all__ = ['defer']


def defer(op: Callable[[], None]):
    """ Defer the given operation on"""
    call_stacks = stack()
    for call in call_stacks[:5]:
        if 'deferrable_deferred_stack' in call.frame.f_locals:
            call.frame.f_locals['deferrable_deferred_stack'].append(op)
            break