# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/gaogaotiantian/dowhen/blob/master/NOTICE

from typing import Any, Callable

from decorator import decorator


def true_guarded_by(cmp: Callable[[int], bool]):
    """
    `true_guarded_by` is a decorator. It first uses the condition
    function to check if the condition is satisfied, and then
    pass the count of satisfying to `cmp`. If `cmp(count)` returns
    True, the do callback will be executed.

    Usage:

        def f():
            for x in range(100):
                print(x)

        @true_guarded_by(lambda count: count <= 5) # count <= 5(limit)
        def check(x):
            return x > 5 # only range(6, 11) takes effect

        do('print(f"x={x}")').when(f, 'print(x)', condition=check)

    `print(f"x={x}")` will only be executed when `x` is in range(6, 11).

    """
    count = 0

    @decorator
    def wrapper(func: Callable[..., bool | Any], *args, **kwargs):
        nonlocal count
        result = func(*args, **kwargs)
        if result:
            count += 1
            return cmp(count)
        return result  # False | DISABLE

    return wrapper
