# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock, Thread, Event, get_ident
import asyncio
import logging

# Third-party modules
from typing import Optional, Dict, Awaitable, Any

# NOC modules
from noc.core.handler import get_handler
from noc.core.ioloop.util import setup_asyncio
from noc.config import config
from .base import DCSBase

DEFAULT_DCS = "consul://%s:%s/%s" % (config.consul.host, config.consul.port, config.consul.base)


class DCSRunner(object):
    HANDLERS = {"consul": "noc.core.dcs.consul.ConsulDCS"}

    def __init__(self):
        self.lock = Lock()
        self.thread: Optional[Thread] = None
        self.loop: Optional[asyncio.BaseEventLoop] = None
        self.instances: Dict[str, DCSBase] = {}
        self.ready_event = Event()
        self.logger = logging.getLogger()

    @classmethod
    def get_dcs_class(cls, url: str):
        scheme = url.split(":", 1)[0]
        if scheme not in cls.HANDLERS:
            raise ValueError("Unknown DCS handler: %s" % scheme)
        handler = get_handler(cls.HANDLERS[scheme])
        if not handler:
            raise ValueError("Cannot initialize DCS handler: %s", scheme)
        return handler

    def get_dcs(self, url: Optional[str] = None) -> DCSBase:
        url = url or DEFAULT_DCS
        with self.lock:
            dcs = self.instances.get(url)
            if not dcs:
                if not self.thread:
                    # Run separate DCS thread
                    self.thread = Thread(name="dcs", target=self._runner)
                    self.thread.daemon = True
                    self.thread.start()
                    self.ready_event.wait()
                    self.logger.debug("DCS runner thread is ready")
                self.logger.debug("Starting DCS %s" % url)
                dcs_cls = self.get_dcs_class(url)
                dcs = dcs_cls(self, url)
                self.instances[url] = dcs
                self.loop.call_soon_threadsafe(self.loop.create_task, dcs.start())
            return dcs

    def _runner(self):
        self.logger.debug("Starting DCS runner thread")
        setup_asyncio()
        self.loop = asyncio.get_event_loop()
        self.ready_event.set()
        self.loop.run_forever()
        self.logger.debug("Stopping DCS runner thread")

    async def trampoline(self, aw: Awaitable) -> Any:
        """
        Trampoline awaitable to dedicated loop
        :param aw:
        :return:
        """

        async def thunk():
            try:
                r = await aw
                loop.call_soon_threadsafe(future.set_result, r)
            except Exception as e:
                loop.call_soon_threadsafe(future.set_exception, e)

        is_same_thread = not self.thread or self.thread.ident == get_ident()
        if is_same_thread:
            return await aw
        # Trampoline to proper thread
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.loop.call_soon_threadsafe(self.loop.create_task, thunk())
        return await future


runner = DCSRunner()


def get_dcs(url=None):
    return runner.get_dcs(url)
