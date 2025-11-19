# ----------------------------------------------------------------------
# Service stub for scripts and commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import threading
from collections import defaultdict
import asyncio
from typing import Optional, Dict, List, Any
from functools import partial
import atexit

# NOC modules
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from noc.config import config
from noc.core.msgstream.client import MessageStreamClient
from noc.core.msgstream.queue import MessageStreamQueue
from noc.core.msgstream.error import MsgStreamError
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
        self.is_publisher_stopped = threading.Event()
        self.config = None
        self.slot_number = 0
        self._metrics = defaultdict(list)
        self.loop: Optional[asyncio.BaseEventLoop] = None
        self.publish_queue: Optional[MessageStreamQueue] = None

    def start(self):
        t = threading.Thread(target=self._start, daemon=True)
        t.start()
        # Wait for IOLoop is ready
        self.is_ready.wait()

    def stop_publisher(self) -> None:
        self.logger.debug("Shutting down publisher")
        self.publish_queue.shutdown()
        self.logger.debug("Waiting for publisher to stop")
        self.is_publisher_stopped.wait()
        self.logger.debug("Publisher is stopped")

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
        return RPCProxy(self, f"{name}-{pool}" if pool else name, sync=sync, hints=hints)

    def iter_rpc_retry_timeout(self):
        """
        Yield timeout to wait after unsuccessful RPC connection
        """
        for t in config.rpc.retry_timeout.split(","):
            yield float(t)

    def register_metrics(self, table: str, data: List[Dict[str, Any]], key: Optional[int] = None):
        self._metrics[table] += data

    def init_publisher(self) -> None:
        ev = threading.Event()
        t = threading.Thread(target=self.publisher, name="publisher", daemon=True, args=(ev,))
        t.start()
        ev.wait()
        atexit.register(self.stop_publisher)

    def publisher(self, ev: threading.Event) -> None:
        """Publisher coroutine."""

        async def inner() -> None:
            self.logger.debug("Running publisher coroutine")
            ev.set()
            async with MessageStreamClient() as client:
                while not self.publish_queue.to_shutdown:
                    req = await self.publish_queue.get(timeout=1)
                    if not req:
                        continue  # Timeout or shutdown
                    try:
                        await client.publish_request(req, wait_for_stream=True)
                    except MsgStreamError as e:
                        self.logger.error("Failed to publish message: %s", e)
                        self.logger.error("Retry message")
                        await asyncio.sleep(1)
                        self.publish_queue.put(req, fifo=False)
            self.logger.debug("Stopping producer coroutine")
            self.is_publisher_stopped.set()

        loop = asyncio.get_event_loop()
        self.publish_queue = MessageStreamQueue(loop)
        loop.run_until_complete(inner())

    def publish(
        self,
        value: bytes,
        stream: str,
        partition: Optional[int] = None,
        key: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ):
        if not self.publish_queue:
            self.init_publisher()
        req = MessageStreamClient.get_publish_request(
            data=value, stream=stream, partition=partition, sharding_key=key, headers=headers
        )
        self.publish_queue.put(req)

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
