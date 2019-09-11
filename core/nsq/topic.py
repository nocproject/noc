# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSQ Topic Queue
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import deque
from threading import Lock, Condition
import datetime

# Third-party modules
import six
import ujson
import tornado.gen
import tornado.locks

# NOC modules
from noc.core.backport.time import perf_counter


class TopicQueue(object):
    def __init__(self, topic):
        self.topic = topic
        self.lock = Lock()
        self.put_condition = Condition()
        self.put_async_condition = tornado.locks.Condition()
        self.queue = deque()  # @todo: maxlen
        self.queue_size = 0
        self.to_shutdown = False
        self.last_get = None
        # Metrics
        self.msg_put = 0
        self.msg_get = 0
        self.msg_put_size = 0
        self.msg_get_size = 0
        self.msg_requeued = 0
        self.msg_requeued_size = 0

    def put(self, message, fifo=True):
        """
        Put message into queue. Block if queue is full

        :param message: Message of any json-serializable type
        :param fifo: Boolean. Append message to the start of queue (LIFO) if False.
            Append message to the end of queue (FIFO) if True.
        :return:
        """
        if not isinstance(message, six.string_types):
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
        with self.put_condition:
            self.put_condition.notify_all()
            self.put_async_condition.notify_all()

    def return_messages(self, messages):
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

    def iter_get(self, n=1, size=None, total_overhead=0, message_overhead=0):
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
        """
        Check if queue is empty

        :return: True if queue is empty, False otherwise
        """
        return not self.queue_size

    def qsize(self):
        """
        Returns amount of messages and size of queue

        :return: messages, total size
        """
        with self.lock:
            return len(self.queue), self.queue_size

    def shutdown(self):
        """
        Begin shutdown sequence. Disable queue writes

        :return:
        """
        if self.to_shutdown:
            raise RuntimeError("Already in shutdown")
        self.to_shutdown = True
        with self.put_condition:
            self.put_condition.notify_all()

    def wait(self, timeout=None):
        """
        Block and wait for new messages up to `timeout`

        :param timeout: Wait timeout. No limit if None
        """
        if self.queue_size:
            return  # Data ready
        with self.put_condition:
            self.put_condition.wait(timeout)

    @tornado.gen.coroutine
    def wait_async(self, timeout=None, rate=None):
        """
        Block and wait up to `timeout`
        :param timeout: Max. wait in seconds
        :param rate: Max. rate of publishing in messages per second
        :return:
        """
        # Sleep to throttle rate
        if rate and self.last_get:
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
                        raise tornado.gen.Return()
        # Check if queue already contains messages
        if not self.queue_size:
            # No messages, wait
            if timeout is not None:
                timeout = datetime.timedelta(seconds=timeout)
            yield self.put_async_condition.wait(timeout)

    def apply_metrics(self, data):
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
