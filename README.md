# deferrable-py

A lightweight pure Python implementation of Go's "defer"

## Why it matters?

Suppose that you want to close a file after a chain of operations. Generally, you can do this.

```python
def func():
    with open('foo.txt', 'r') as fp:
        fp.write('abcdef123456')
    # NOTE: fp is now closed as the code exits the context of "open()".
    # NOTE: At this point, fp is no longer useful.
# end of def
```

However, what if `fp` is still needed later in the same method.

With this library, you can simply defer `fp.close()` to the end of callable invocation.

```python
from deferrable import defer, deferrable


@deferrable
def func():
    fp = open('foo.txt', 'r')
    defer(lambda: fp.close())  # <-- Define a deferred operation
    # NOTE: You can also simply write:
    #
    #         defer(functools.partial(lambda fp: fp.close(), fp))
    #
    #       if you want to deal with the late binding problem right away.

    fp.write('abcdef123456')

    ...

    # NOTE: No more code here
# end of def
```

When the invocation of `func()` completes successfully or ends with error, the deferred operation will be invoked.

> Please note that the deferred operation will not alter the returned value of the deferrable callable.

## API

(TODO Write it here)

