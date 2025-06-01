# deferrable-py

A lightweight pure-Python implementation of Go's "defer"

> This is not yet supported `asyncio`
.
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

## Example Use Cases

* Flexible cleanup for each test case
  ```python
  from unittest import TestCase
  
  from deferrable import defer, deferrable
  
  def create_obj(id):
    ...
  
  def delete_obj(id):
    ...
  
  class UnitTest(TestCase):
    @deferrable
    def test_happy_path(self):
      o = create_obj('alpha')  # <-- create a test obj
      defer(lambda: delete_obj('alpha'))  # <-- defer the test obj deletion to the end 
      ... # <-- the rest of the test
  ```
* Handle the data temporarily.
  ```python
  from os import unlink
  from typing import Iterator
  from deferrable import defer, deferrable
  
  def load_blob(url) -> Iterator[bytes]:
    ...
  
  def upload_blob(local_file_path):
    ...
  
  @deferrable
  def transfer(source_url, destination_url):
    tmp_file_path = ...
    with open(tmp_file_path, 'wb') as f:
      for b in load_blob(source_url):
        f.write(b)
    defer(lambda: unlink(tmp_file_path))
    upload_blob(tmp_file_path)
  ```

## API Reference

### Decorator `deferrable.deferrable(func: Callable)`

Make the wrapped callable capable of having deferred operations.

The `func` parameter must be callable.

```python
from deferrable import deferrable

@deferrable
def func_a():
    ...
```

### Function `deferrable.defer(op: Callable[[], None])`

Defer the given operation to be executed at the end of the callable invocation,i.e., on the call exit.

The `op` parameter must be a callable which takes no parameters. Any returning values will be disregarded. 

```python
from deferrable import deferrable, defer

@deferrable
def func_a():
    ...
    defer(lambda: ...)
```

