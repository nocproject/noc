# ----------------------------------------------------------------------
# Various IOLoop utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import asyncio
import logging

# Third-party modules
from typing import Callable, TypeVar, Tuple, Any, Optional

# NOC modules
from noc.config import config
from noc.core.comp import reraise

logger = logging.getLogger(__name__)
T = TypeVar("T")

USE_UVLOOP = False

if config.features.use_uvloop:
    try:
        import uvloop

        USE_UVLOOP = True
    except ImportError:
        pass


class IOLoopContext(object):
    def __init__(self, suppress_trace=False):
        self.prev_loop = None
        self.new_loop = None
        self.suppress_trace = suppress_trace

    def get_context(self):
        self.prev_loop = asyncio._get_running_loop()
        self.new_loop = asyncio.new_event_loop()
        if self.prev_loop:
            # Reset running loop
            asyncio._set_running_loop(None)
        return self.new_loop

    def drop_context(self):
        # Cancel all tasks
        to_cancel = asyncio.all_tasks(self.new_loop)
        for task in to_cancel:
            task.cancel()
        asyncio.gather(*to_cancel, return_exceptions=True)
        self.new_loop.run_until_complete(self.new_loop.shutdown_asyncgens())
        #
        self.new_loop.close()
        self.new_loop = None
        asyncio._set_running_loop(self.prev_loop)
        if self.prev_loop:
            asyncio._set_running_loop(self.prev_loop)
        else:
            asyncio._set_running_loop(None)
            asyncio.get_event_loop_policy().reset_called()
        self.prev_loop = None

    def get_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        return self.new_loop

    def __enter__(self):
        return self.get_context()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.drop_context()
        if self.suppress_trace:
            return True


def run_sync(cb: Callable[..., T], close_all: bool = True) -> T:
    """
    Run callable on dedicated IOLoop in safe manner
    and return result or raise error

    :param cb: Callable to be runned on IOLoop
    :param close_all: Close all file descriptors
    :return: Callable result
    """
    global _setup_completed

    async def wrapper():
        nonlocal result, error
        try:
            result = await cb()
        except Exception:
            error = sys.exc_info()

    if not _setup_completed:
        setup_asyncio()

    result: Optional[T] = None
    error: Optional[Tuple[Any, Any, Any]] = None

    with IOLoopContext() as loop:
        loop.run_until_complete(wrapper())
    if error:
        reraise(*error)
    return result


_setup_completed = False


def setup_asyncio() -> None:
    """
    Initial setup of asyncio

    :return:
    """
    global _setup_completed, USE_UVLOOP

    if _setup_completed:
        return
    logger.info("Setting up asyncio event loop policy")
    if USE_UVLOOP:
        logger.info("Setting up uvloop event loop")
        asyncio.set_event_loop_policy(NOCEventUVLoopPolicy())
    elif config.features.use_uvloop:
        logger.info("uvloop is not installed, using default event loop")
        asyncio.set_event_loop_policy(NOCEventLoopPolicy())
    else:
        logger.info("Setting up default event loop")
        asyncio.set_event_loop_policy(NOCEventLoopPolicy())
    _setup_completed = True


class NOCEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        try:
            return super().get_event_loop()
        except RuntimeError:
            loop = self.new_event_loop()
            self.set_event_loop(loop)
            return loop

    def reset_called(self) -> None:
        """
        Reset called status
        :return:
        """
        self._local._set_called = False


if USE_UVLOOP:

    class NOCEventUVLoopPolicy(uvloop.EventLoopPolicy):
        def get_event_loop(self) -> asyncio.AbstractEventLoop:
            try:
                return super().get_event_loop()
            except RuntimeError:
                loop = self.new_event_loop()
                self.set_event_loop(loop)
                return loop

        def reset_called(self) -> None:
            """
            Reset called status
            :return:
            """
            self._local._set_called = False
