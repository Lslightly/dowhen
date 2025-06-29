# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/gaogaotiantian/dowhen/blob/master/NOTICE

from typing import Callable

import pytest
from decorator import decorator

from dowhen import do, when
from dowhen.decorators import true_guarded_by


def f():
    for x in range(20):
        print(x)


def test_true_guarded_by():
    def logging(x):
        nonlocal logging_times
        logging_times += 1
        print(f"INFO: {x}")

    cmp: Callable[[int], bool]
    for cmp, expect_times in [
        (lambda count: count < 10, 9),
        (lambda count: count < 20, 14),
        (lambda count: count > 10, 4),
    ]:

        @true_guarded_by(cmp)
        def check(x):
            return x > 5  # [6, 19], 14 times

        handler = do(logging).when(f, "print(x)", condition=check)
        logging_times = 0
        f()
        assert logging_times == expect_times
        handler.remove()


def test_usage_true_guarded_by():
    def f(x):
        return x

    @true_guarded_by(lambda count: count > 1)
    def check(x):
        return x == 0

    when(f, "return x", condition=check).do("x = 1")
    assert f(0) == 0  # x = 1 is not executed because count is 1
    assert f(0) == 1  # x is set to 1 because count is 2


def test_isolated_counter():
    def check(x):
        return x > 5

    def f(stream: int):
        res = 0
        for x in range(stream):
            if x < 10:
                res += x
            if x < 20:
                res = res - x
        return res

    total_count = 0

    def logging():
        nonlocal total_count
        total_count += 1

    count_predicate = lambda count: count < 3
    do(logging).when(
        f, "res += x", condition=true_guarded_by(count_predicate)(check)
    )  # print 2 times
    do(logging).when(
        f, "res = res - x", condition=true_guarded_by(count_predicate)(check)
    )  # print 2 times
    f(20)
    assert total_count == 4


def test_shared_counter():
    @true_guarded_by(lambda count: count < 3)
    def check(x):
        return x > 5

    def f(stream: int):
        res = 0
        for x in range(stream):
            if x < 10:
                res += x
            if x < 20:
                res = res - x
        return res

    total_count = 0

    def logging():
        nonlocal total_count
        total_count += 1

    do(logging).when(f, "res += x", condition=check)  # print 2 times
    do(logging).when(f, "res = res - x", condition=check)  # print 2 times
    f(20)
    assert total_count == 2


def test_decorator_do():
    @decorator
    def logging(func, *args, **kwargs):
        print("LOG::", end="")
        return func(*args, **kwargs)

    @logging
    def info(x):
        nonlocal logging_times
        logging_times += 1
        print(f"INFO: {x}")

    do(info).when(f, "print(x)", condition="x > 5")
    logging_times = 0
    f()
    assert logging_times == 14


def test_native_decorator_do_raise_exception():
    with pytest.raises(TypeError):

        def logging(func):
            def wrapper(*args, **kwargs):
                print("LOG::", end="")
                return func(*args, **kwargs)

            return wrapper

        @logging
        def info(x):
            print(f"INFO: {x}")

        do(info).when(f, "print(x)", condition="x > 5")
        f()
