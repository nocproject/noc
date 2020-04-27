# ----------------------------------------------------------------------
# Various IOLoop utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys

# Third-party modules
from typing import Callable, TypeVar, List, Tuple, Any
from tornado.ioloop import IOLoop
import tornado.gen

# NOC modules
from noc.core.comp import reraise

T = TypeVar("T")


def run_sync(cb: Callable[..., T], close_all: bool = True) -> T:
    """
    Run callable on dedicated IOLoop in safe manner
    and return result or raise error

    :param cb: Callable to be runned on IOLoop
    :param close_all: Close all file descriptors
    :return: Callable result
    """

    @tornado.gen.coroutine
    def wrapper():
        try:
            r = yield cb()
            result.append(r)
        except Exception:
            error.append(sys.exc_info())

    result: List[T] = []
    error: List[Tuple[Any, Any, Any]] = []

    # Get current instance or None
    prev_io_loop = IOLoop.current(instance=False)
    # Instantiate new IOLoop
    ioloop = IOLoop()
    ioloop.make_current()
    try:
        ioloop.run_sync(wrapper)
    finally:
        ioloop.close(all_fds=close_all)
        if prev_io_loop:
            prev_io_loop.make_current()
        else:
            IOLoop.clear_current()
    if error:
        reraise(*error[0])
    return result[0]
