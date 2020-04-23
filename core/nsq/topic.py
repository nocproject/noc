# ----------------------------------------------------------------------
# NSQ Topic Queue
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import deque
from threading import Lock
import datetime

# Third-party modules
import ujson
import tornado.gen
import tornado.locks
import tornado.ioloop
from typing import Union, Iterable, List, Dict, Any, Optional

# NOC modules
from noc.config import config
from noc.core.backport.time import perf_counter


class TopicQueue(object):
    def __init__(self, topic: str, io_loop: Optional[tornado.ioloop.IOLoop] = None) -> None:
        self.topic = topic
        self.lock = Lock()
        self.put_condition = tornado.locks.Condition()
        self.shutdown_complete = tornado.locks.Event()
        self.queue: deque = deque()
        self.queue_size = 0
        self.to_shutdown = False
        self.last_get = None
        self.io_loop = io_loop
        # Metrics
        self.msg_put = 0
        self.msg_get = 0
        self.msg_put_size = 0
        self.msg_get_size = 0
        self.msg_requeued = 0
        self.msg_requeued_size = 0

    @staticmethod
    def iter_encode_chunks(
        message: Union[str, object], limit: int = config.nsqd.mpub_size - 8
    ) -> Iterable[str]:
        """
        Encode data to iterable atomic chunks of up to limit size

        :param message: Input data
        :param limit: Chunk limit
        :return: Yields JSON-encoded chunks
        :raises ValueError: If message cannot be encoded or too big
        """
        if isinstance(message, str):
            if len(message) > limit:
                raise ValueError("Message too big")
            yield message
        else:
            data = ujson.dumps(message)
            if len(data) <= limit:
                yield data
            elif isinstance(message, (list, tuple)):
                # Try to split in parts
                n_chunks = len(data) // limit + 1
                chunk_size = len(message) // n_chunks
                while message:
                    chunk, message = message[:chunk_size], message[chunk_size:]
                    chunk_data = ujson.dumps(chunk)
                    if len(chunk_data) > limit:
                        raise ValueError("Message too big")
                    yield chunk_data
            else:
                raise ValueError("Message too big")

    def put(self, message: object, fifo: bool = True) -> None:
        """
        Put message into queue. Block if queue is full

        :param message: Message of any json-serializable type
        :param fifo: Boolean. Append message to the start of queue (LIFO) if False.
            Append message to the end of queue (FIFO) if True.
        :return:
        """
        if not isinstance(message, str):
            message = ujson.dumps(message)
        with self.lock:
            if self.to_shutdown:
                raise RuntimeError("put() after shutdown")
            if fifo:
                self.queue.append(message)
            else:
                self.queue.appendleft(message)
            m_size = len(message)
            self.queue_size += m_size
            self.msg_put += 1
            self.msg_put_size += m_size
            # Unblock waiters in main thread
            if self.io_loop:
                # Execute in the main thread
                self.io_loop.add_callback(self._notify_all)
            else:
                self._notify_all()

    def _notify_all(self):
        self.put_condition.notify_all()

    def return_messages(self, messages: List[str]) -> None:
        """
        Return messages to the start of the queue

        :param messages: List of messages
        :return:
        """
        with self.lock:
            if self.to_shutdown:
                raise RuntimeError("return_messages() after shutdown")
            for msg in reversed(messages):
                self.queue.appendleft(msg)
                self.msg_requeued += 1
                self.msg_requeued_size += len(msg)
            # Unblock waiters in main thread
            self.put_condition.notify_all()

    def iter_get(
        self, n: int = 1, size: int = None, total_overhead: int = 0, message_overhead: int = 0
    ) -> Iterable[str]:
        """
        Get up to `n` items up to `size` size.

        Warning queue will be locked until the end of function call.

        :param n: Amount of items returned
        :param size: None - unlimited, integer - upper size limit
        :param total_overhead: Adjust total size to `total_overhead` octets.
        :param message_overhead: Adjust total size to `message_overhead` per each returned message.
        :return: Yields items
        """
        total = 0
        if size and total_overhead:
            total += total_overhead
        with self.lock:
            for _i in range(n):
                try:
                    msg = self.queue.popleft()
                    m_size = len(msg)
                    total += m_size
                    if size and message_overhead:
                        total += message_overhead
                    if size and total > size:
                        # Size limit exceeded. Return message to queue
                        self.queue.appendleft(msg)
                        break
                    self.queue_size -= m_size
                    self.msg_get += 1
                    self.msg_get_size += m_size
                    yield msg
                except IndexError:
                    break
            self.last_get = perf_counter()

    def is_empty(self):
        # () -> bool
        """
        Check if queue is empty

        :return: True if queue is empty, False otherwise
        """
        return not self.queue_size

    def qsize(self):
        # () -> int
        """
        Returns amount of messages and size of queue

        :return: messages, total size
        """
        with self.lock:
            return len(self.queue), self.queue_size

    def shutdown(self):
        # () -> ()
        """
        Begin shutdown sequence. Disable queue writes

        :return:
        """
        if self.to_shutdown:
            raise RuntimeError("Already in shutdown")
        self.to_shutdown = True
        with self.lock:
            self.put_condition.notify_all()

    @tornado.gen.coroutine
    def wait(self, timeout=None, rate=None):
        # (Optional[float], Optional[int]) -> None
        """
        Block and wait up to `timeout`
        :param timeout: Max. wait in seconds
        :param rate: Max. rate of publishing in messages per second
        :return:
        """
        # Sleep to throttle rate
        if rate and self.last_get and not self.to_shutdown:
            now = perf_counter()
            delta = max(self.last_get + 1.0 / rate - now, 0)
            if delta > 0:
                yield tornado.gen.sleep(delta)
                # Adjust remaining timeout
                if timeout:
                    # Adjust timeout
                    timeout -= delta
                    if timeout <= 0:
                        # Timeout expired
                        return
        # Check if queue already contains messages
        if not self.queue_size and not self.to_shutdown:
            # No messages, wait
            if timeout is not None:
                timeout = datetime.timedelta(seconds=timeout)
            yield self.put_condition.wait(timeout)

    def apply_metrics(self, data: Dict[str, Any]) -> None:
        data.update(
            {
                ("nsq_msg_put", ("topic", self.topic)): self.msg_put,
                ("nsq_msg_put_size", ("topic", self.topic)): self.msg_put_size,
                ("nsq_msg_get", ("topic", self.topic)): self.msg_get,
                ("nsq_msg_get_size", ("topic", self.topic)): self.msg_get_size,
                ("nsq_msg_requeued", ("topic", self.topic)): self.msg_requeued,
                ("nsq_msg_requeued_size", ("topic", self.topic)): self.msg_requeued_size,
            }
        )
