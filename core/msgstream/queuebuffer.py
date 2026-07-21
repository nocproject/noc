# ----------------------------------------------------------------------
# QueueBuffer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Any, Iterable
from threading import Lock

# Third-party modules
import orjson

# Python modules
from noc.config import config


class QBuffer:
    """
    Buffered writes to queue, merge outgoing messages to a larger block
    """

    def __init__(self, max_size: int | None = None) -> None:
        self.buf: defaultdict[tuple[str, int], list[bytes]] = defaultdict(list)
        self.lock = Lock()
        self.max_size = max_size or config.liftbridge.max_message_size

    def put(self, stream: str, partition: int, data: list[dict[str, Any]]):
        """
        Put block of data to buffer
        :return:
        """
        if not data:
            return
        d = [orjson.dumps(x) for x in data]
        with self.lock:
            self.buf[stream, partition] += d

    @staticmethod
    def _iter_chunks(data: list[bytes], max_size: int) -> Iterable[bytes]:
        r: list[bytes] = []
        size = 0
        for d in data:
            ld = len(d)
            if size + ld + 1 > max_size and r:
                yield b"\n".join(r)
                r = []
                size = 0
            r.append(d)
            size += ld + (1 if size else 0)
        if r:
            yield b"\n".join(r)

    def iter_slice(self) -> Iterable[tuple[str, int, bytes]]:
        """
        Iterates tuple of (stream, partition, data)
        :return:
        """
        with self.lock:
            for (stream, partition), out in self.buf.items():
                for chunk in self._iter_chunks(out, self.max_size):
                    yield stream, partition, chunk
            self.buf = defaultdict(list)

    def is_empty(self) -> bool:
        """
        Check if buffer is empty
        :return:
        """
        with self.lock:
            return bool(self.buf)
