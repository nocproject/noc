# ----------------------------------------------------------------------
# MXMessageBuffer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import deque
from typing import Dict, Any, Optional, Iterable
from threading import Lock
import math

# Third-party modules
import orjson

# Python modules
from noc.core.mx import Message
from noc.config import config


class MBuffer(object):
    """
    Buffered writes to queue, merge outgoing messages to a larger block
    """

    def __init__(
        self,
        max_size: Optional[int] = None,
    ):
        self.queue: deque = deque()
        self.buf: Dict[str, Any] = {}
        self.lock = Lock()
        self.req_puts: int = 0
        self.req_gets: int = 0
        self.max_size = max_size or config.msgstream.max_message_size

    def put(self, msg: Message, group_key: Optional[str] = None):
        """
        Put block of data to buffer
        :param msg:
        :param group_key:
        :return:
        """
        if not msg.value:
            return
        with self.lock:
            if group_key and group_key in self.buf:
                self.buf[group_key] += [msg.value]
                return
            if group_key:
                self.buf[group_key] = []
            self.queue.append((group_key or "", msg))

    @staticmethod
    def _iter_chunks(a, n):
        k, m = divmod(len(a), n)
        for i in range(n):
            yield orjson.dumps(a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)])

    def iter_slice(self) -> Iterable[Message]:
        """
        Iterates tuple of (stream, partition, data)
        :return:
        """
        r_size = self.qsize()
        while r_size:
            r_size -= 1
            with self.lock:
                group_key, msg = self.queue.popleft()
            if not group_key or group_key not in self.buf:
                yield msg
                continue
            v = [msg.value] + self.buf.pop(group_key)
            for v in self._iter_chunks(v, math.ceil(len(orjson.dumps(v)) / self.max_size)):
                msg.value = v
                yield msg

    def is_empty(self) -> bool:
        """
        Check if buffer is empty
        :return:
        """
        with self.lock:
            return bool(self.qsize())

    def qsize(self) -> int:
        with self.lock:
            return len(self.queue)
