#!./bin/python
# ----------------------------------------------------------------------
# Write channel service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from time import perf_counter
from urllib.parse import quote as urllib_quote

# Third-party modules
from typing import Optional, List

# NOC modules
from noc.config import config
from noc.core.msgstream.message import Message


class Channel(object):
    def __init__(self, service, table: str):
        self.service = service
        self.table = table
        self.stream = f"ch.{table}"
        self.last_offset: int = 0
        self.data: List[bytes] = []
        self.size: int = 0
        self.records: int = 0
        self.expired: Optional[float] = None
        self.q_sql = urllib_quote(f"INSERT INTO raw_{table} FORMAT JSONEachRow".encode("utf-8"))
        self.feed_ready = asyncio.Event()
        self.feed_ready.set()
        self.ttl = float(config.chwriter.batch_delay_ms) / 1_000.0

    async def feed(self, msg: Message):
        """
        Feed the message. Returns optional offset of last saved message.
        :param msg:
        :return:
        """
        # Wait until feed became possible
        await self.feed_ready.wait()
        # Append data
        self.data.append(msg.value)
        self.size += len(msg.value)
        self.records += msg.value.count(b"\n") + (0 if msg.value.endswith(b"\n") else 1)
        self.last_offset = msg.offset
        if not self.expired:
            self.expired = perf_counter() + self.ttl
        if self.is_ready_to_flush():
            await self.schedule_flush()
            await self.feed_ready.wait()

    def is_expired(self, ts: float) -> bool:
        """
        Check if channel is expired to given timestamp
        :param ts:
        :return:
        """
        return self.expired and self.expired < ts

    def is_ready_to_flush(self) -> bool:
        """
        Check if channel is ready to flush
        """
        if not self.size:
            return False
        return self.records >= config.chwriter.batch_size

    async def schedule_flush(self):
        if not self.feed_ready.is_set():
            return  # Already scheduled
        self.expired = None
        self.feed_ready.clear()
        await self.service.flush_queue.put(self)

    def flush_complete(self):
        """
        Called when data are safely flushed
        :return:
        """
        self.data = []
        self.size = 0
        self.records = 0
        self.expired = None
        self.feed_ready.set()

    def get_data(self) -> bytes:
        """
        Get chunk of spooled data

        :return:
        """
        return b"\n".join(self.data)
