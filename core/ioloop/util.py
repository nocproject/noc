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
from typing import Callable, TypeVar, List, Tuple, Any, Optional

# NOC modules
from noc.config import config
from noc.core.comp import reraise

logger = logging.getLogger(__name__)
T = TypeVar("T")


class IOLoopContext(object):
    def __init__(self):
        self.prev_loop = None
        self.new_loop = None

    def get_context(self):
        self.prev_loop = asyncio._get_running_loop()
        self.new_loop = asyncio.new_event_loop()
        if self.prev_loop:
            # Reset running loop
            asyncio._set_running_loop(None)
        return self.new_loop

    def drop_context(self):
        # Cancel all tasks
        to_cancel = asyncio.Task.all_tasks(self.new_loop)
        for task in to_cancel:
            task.cancel()
        asyncio.gather(*to_cancel, loop=self.new_loop, return_exceptions=True)
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
        try:
            result.append(await cb())
        except Exception:
            error.append(sys.exc_info())

    if not _setup_completed:
        setup_asyncio()

    result: List[T] = []
    error: List[Tuple[Any, Any, Any]] = []

    with IOLoopContext() as loop:
        loop.run_until_complete(wrapper())
    if error:
        reraise(*error[0])
    return result[0]


_setup_completed = False


def setup_asyncio() -> None:
    """
    Initial setup of asyncio

    :return:
    """
    global _setup_completed

    if _setup_completed:
        return
    logger.info("Setting up asyncio event loop policy")
    if config.features.use_uvlib:
        try:
            import uvloop

            logger.info("Setting up libuv event loop")
            uvloop.install()
        except ImportError:
            logger.info("libuv is not installed, using default event loop")
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


if sys.version_info >= (3, 7):

    def get_future_loop(future: asyncio.Future) -> asyncio.AbstractEventLoop:
        return future.get_loop()


else:

    def get_future_loop(future: asyncio.Future) -> asyncio.AbstractEventLoop:
        return future._loop
