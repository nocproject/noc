# ----------------------------------------------------------------------
# Service stub for scripts and commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import threading
from collections import defaultdict
import asyncio
from typing import Optional, Dict, List, Any
from functools import partial

# NOC modules
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from noc.config import config
from noc.core.msgstream.client import MessageStreamClient
from noc.core.ioloop.util import run_sync
from noc.core.mx import MX_STREAM, MessageType
from noc.core.router.base import Router
from .rpc import RPCProxy


class ServiceStub(object):
    name = "stub"
    pooled = False

    def __init__(self):
        self.logger = logging.getLogger("stub")
        self.is_ready = threading.Event()
        self.config = None
        self.slot_number = 0
        self._metrics = defaultdict(list)
        self.loop: Optional[asyncio.BaseEventLoop] = None

    def start(self):
        t = threading.Thread(target=self._start)
        t.setDaemon(True)
        t.start()
        self.is_ready.wait()

    def _start(self):
        self.loop = asyncio.get_event_loop()
        # Initialize DCS
        self.dcs = get_dcs(DEFAULT_DCS)
        # Activate service
        self.logger.warning("Activating stub service")
        self.logger.warning("Starting IOLoop")
        self.loop.call_soon(self.is_ready.set)
        self.loop.run_forever()

    def get_event_loop(self) -> asyncio.BaseEventLoop:
        return self.loop

    def open_rpc(self, name, pool=None, sync=False, hints=None):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc, sync=sync, hints=hints)

    def iter_rpc_retry_timeout(self):
        """
        Yield timeout to wait after unsuccessful RPC connection
        """
        for t in config.rpc.retry_timeout.split(","):
            yield float(t)

    def register_metrics(self, table: str, data: List[Dict[str, Any]], key: Optional[int] = None):
        self._metrics[table] += data

    def publish(
        self,
        value: bytes,
        stream: str,
        partition: Optional[int] = None,
        key: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ):
        async def wrap():
            async with MessageStreamClient() as client:
                await client.publish(
                    value=value,
                    stream=stream,
                    partition=partition,
                    key=key,
                    headers=headers,
                )

        run_sync(wrap)

    async def send_message(
        self,
        data: Any,
        message_type: MessageType,
        headers: Optional[Dict[str, bytes]] = None,
        sharding_key: int = 0,
    ):
        """
        Build message and schedule to send to mx service

        :param data: Data for transmit
        :param message_type: Message type
        :param headers: additional message headers
        :param sharding_key: Key for sharding over MX services
        :return:
        """
        msg = Router.get_message(data, message_type.value, headers, sharding_key)
        self.logger.debug("Send message: %s", msg)
        self.publish(value=msg.value, stream=MX_STREAM, partition=0, headers=msg.headers)

    async def get_stream_partitions(self, stream: str) -> int:
        """

        :param stream:
        :return:
        """
        async with MessageStreamClient() as client:
            while True:
                meta = await client.fetch_metadata()
                if meta.metadata:
                    if stream in meta.metadata:
                        if meta.metadata[stream]:
                            return len(meta.metadata[stream])
                        break
                # Cluster election in progress or cluster is misconfigured
                self.logger.info("Stream '%s' has no active partitions. Waiting" % stream)
                await asyncio.sleep(1)

    @staticmethod
    def get_slot_limits(slot_name):
        """
        Get slot count
        :param slot_name:
        :return:
        """
        dcs = get_dcs(DEFAULT_DCS)
        return run_sync(partial(dcs.get_slot_limit, slot_name))
