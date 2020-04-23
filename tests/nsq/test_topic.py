# ----------------------------------------------------------------------
# Test NSQ TopicQueue
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import tornado.gen
import tornado.ioloop
import tornado.locks

# NOC modules
from noc.core.nsq.topic import TopicQueue


@pytest.mark.parametrize("items,expected", [([], True), ([1], False), ([1, 2], False)])
def test_is_empty(items, expected):
    queue = TopicQueue("test_is_empty")
    for item in items:
        queue.put(item)
    assert queue.is_empty() is expected


@pytest.mark.parametrize(
    "put_kwargs,expected",
    [
        # Empty
        ([], []),
        # Single FIFO
        ([{"message": 1}], ["1"]),
        # Multi FIFO
        ([{"message": 1}, {"message": 2}, {"message": 3}], ["1", "2", "3"]),
        # Single LIFO
        ([{"message": 1, "fifo": False}], ["1"]),
        # Multi LIFO
        (
            [
                {"message": 1, "fifo": False},
                {"message": 2, "fifo": False},
                {"message": 3, "fifo": False},
            ],
            ["3", "2", "1"],
        ),
        # Mixed FIFO/LIFO
        (
            [
                {"message": 1, "fifo": True},
                {"message": 2, "fifo": False},
                {"message": 3, "fifo": True},
                {"message": 4, "fifo": False},
            ],
            ["4", "2", "1", "3"],
        ),
    ],
)
def test_put_order(put_kwargs, expected):
    queue = TopicQueue("test_put_order")
    for kw in put_kwargs:
        queue.put(**kw)
    result = list(queue.iter_get(len(put_kwargs)))
    assert result == expected


@pytest.mark.parametrize(
    "input,get_kwargs,expected",
    [
        # Empty
        ([], {"n": 1}, []),
        #  Get  one
        (["1", "2", "3"], {"n": 1}, ["1"]),
        # Get two
        (["1", "2", "3"], {"n": 2}, ["1", "2"]),
        # Get three
        (["1", "2", "3"], {"n": 3}, ["1", "2", "3"]),
        # Get more, cutoff by number
        (["1", "2", "3"], {"n": 4}, ["1", "2", "3"]),
        # Limit by size
        (["11", "22", "33"], {"n": 1, "size": 2}, ["11"]),
        (["11", "22", "33"], {"n": 2, "size": 2}, ["11"]),
        (["11", "22", "33"], {"n": 3, "size": 3}, ["11"]),
        (["11", "22", "33"], {"n": 3, "size": 4}, ["11", "22"]),
        (["11", "22", "33"], {"n": 3, "size": 8}, ["11", "22", "33"]),
        (["11", "22", "33"], {"n": 4, "size": 10}, ["11", "22", "33"]),
        # Limit with overheads
        (
            ["11", "22", "33"],
            {"n": 4, "size": 16, "total_overhead": 4, "message_overhead": 4},
            ["11", "22"],
        ),
    ],
)
def test_get_limit(input, get_kwargs, expected):
    queue = TopicQueue("test_get_limit")
    for msg in input:
        queue.put(msg)
    result = list(queue.iter_get(**get_kwargs))
    assert result == expected


def test_qsize():
    queue = TopicQueue("test_qsize")
    # Empty queue
    assert queue.qsize() == (0, 0)
    qn = 0
    qs = 0
    # Put
    for i in range(10):
        msg = "x" * (i + 1)
        qs += len(msg)
        qn += 1
        queue.put(msg)
        assert queue.qsize() == (qn, qs)
    # Pull
    while qn > 0:
        msg = list(queue.iter_get())[0]
        qn -= 1
        qs -= len(msg)
        assert queue.qsize() == (qn, qs)
    # Empty queue
    assert queue.qsize() == (0, 0)


def test_shutdown():
    queue = TopicQueue("test_shutdown")
    # Fill queue  with 10 items
    to_produce = ["%04d" % i for i in range(10)]
    for msg in to_produce:
        queue.put(msg)
    # Consume 5 of them
    consumed = []
    consumed += list(queue.iter_get(5))
    # Shutdown the queue
    queue.shutdown()
    # Try to shutdown queue twice, raise Runtime error
    with pytest.raises(RuntimeError):
        queue.shutdown()
    # Try to put an item, raise Runtime error
    with pytest.raises(RuntimeError):
        queue.put("9999")
    # Try to return a message, raise Runtime error
    with pytest.raises(RuntimeError):
        queue.return_messages(["9999"])
    # Consume all other items
    consumed += list(queue.iter_get(10))
    # Check all items are consumed
    assert to_produce == consumed


def test_wait():
    @tornado.gen.coroutine
    def producer():
        for msg in to_produce:
            queue.put(msg)
            yield tornado.gen.sleep(sleep_timeout)
        queue.shutdown()

    @tornado.gen.coroutine
    def consumer():
        while not queue.to_shutdown or queue.qsize()[0]:
            yield queue.wait(1)
            consumed["data"] += list(queue.iter_get(100))
        io_loop.stop()

    sleep_timeout = 0.1
    to_produce = ["%04d" % i for i in range(10)]
    consumed = {"data": []}
    queue = TopicQueue("test_wait")
    io_loop = tornado.ioloop.IOLoop()
    io_loop.add_callback(producer)
    io_loop.add_callback(consumer)
    io_loop.start()
    assert to_produce == consumed["data"]


@pytest.mark.parametrize("sleep_timeout", [0.1, 0.55])
def test_wait_throttling(sleep_timeout):
    @tornado.gen.coroutine
    def producer():
        for msg in to_produce:
            queue.put(msg)
            yield tornado.gen.sleep(sleep_timeout)
        queue.shutdown()

    @tornado.gen.coroutine
    def consumer():
        while not queue.to_shutdown or queue.qsize()[0]:
            yield queue.wait(rate=rate)
            consumed["data"] += list(queue.iter_get(100))
            consumed["n_reads"] += 1
        io_loop.stop()

    rate = 4
    n_writes = 10
    dt = n_writes * sleep_timeout
    to_produce = ["%04d" % i for i in range(n_writes)]
    consumed = {"data": [], "n_reads": 0}
    queue = TopicQueue("test_wait")
    io_loop = tornado.ioloop.IOLoop()
    io_loop.add_callback(producer)
    io_loop.add_callback(consumer)
    io_loop.start()
    assert to_produce == consumed["data"]
    assert consumed["n_reads"] <= dt * rate + 2


def test_metrics():
    queue = TopicQueue("test_metrics")
    k = ("topic", queue.topic)
    # Initial metrics are zeroed
    metrics = {"other": 1}
    queue.apply_metrics(metrics)
    assert metrics.get("other") == 1  # Untouched
    assert metrics.get(("nsq_msg_put", k)) == 0
    assert metrics.get(("nsq_msg_put_size", k)) == 0
    assert metrics.get(("nsq_msg_get", k)) == 0
    assert metrics.get(("nsq_msg_get_size", k)) == 0
    assert metrics.get(("nsq_msg_requeued", k)) == 0
    assert metrics.get(("nsq_msg_requeued_size", k)) == 0
    # Put 100 messages of 10 octets each
    for i in range(100):
        msg = "%10d" % i
        queue.put(msg)
    queue.apply_metrics(metrics)
    assert metrics.get("other") == 1  # Untouched
    assert metrics.get(("nsq_msg_put", k)) == 100
    assert metrics.get(("nsq_msg_put_size", k)) == 1000
    assert metrics.get(("nsq_msg_get", k)) == 0
    assert metrics.get(("nsq_msg_get_size", k)) == 0
    assert metrics.get(("nsq_msg_requeued", k)) == 0
    assert metrics.get(("nsq_msg_requeued_size", k)) == 0
    # Get 50 messages of 10 octets each
    msgs = list(queue.iter_get(50))
    queue.apply_metrics(metrics)
    assert metrics.get("other") == 1  # Untouched
    assert metrics.get(("nsq_msg_put", k)) == 100
    assert metrics.get(("nsq_msg_put_size", k)) == 1000
    assert metrics.get(("nsq_msg_get", k)) == 50
    assert metrics.get(("nsq_msg_get_size", k)) == 500
    assert metrics.get(("nsq_msg_requeued", k)) == 0
    assert metrics.get(("nsq_msg_requeued_size", k)) == 0
    # Return 10 messages back to queue
    queue.return_messages(msgs[:10])
    queue.apply_metrics(metrics)
    assert metrics.get("other") == 1  # Untouched
    assert metrics.get(("nsq_msg_put", k)) == 100
    assert metrics.get(("nsq_msg_put_size", k)) == 1000
    assert metrics.get(("nsq_msg_get", k)) == 50
    assert metrics.get(("nsq_msg_get_size", k)) == 500
    assert metrics.get(("nsq_msg_requeued", k)) == 10
    assert metrics.get(("nsq_msg_requeued_size", k)) == 100
    # Get 60 messages (50 left + 10 returned)
    list(queue.iter_get(60))
    queue.apply_metrics(metrics)
    assert metrics.get("other") == 1  # Untouched
    assert metrics.get(("nsq_msg_put", k)) == 100
    assert metrics.get(("nsq_msg_put_size", k)) == 1000
    assert metrics.get(("nsq_msg_get", k)) == 110
    assert metrics.get(("nsq_msg_get_size", k)) == 1100
    assert metrics.get(("nsq_msg_requeued", k)) == 10
    assert metrics.get(("nsq_msg_requeued_size", k)) == 100
