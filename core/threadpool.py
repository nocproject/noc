# ----------------------------------------------------------------------
# ThreadPool class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import logging
import itertools
import time
from collections import deque
import _thread
from time import perf_counter
import asyncio

# Third-party modules
from typing import Optional, Dict, Any, Set, List, Callable, TypeVar

# NOC modules
from noc.config import config
from noc.core.span import Span, get_current_span
from noc.core.error import NOCError

T = TypeVar("T")

logger = logging.getLogger(__name__)

DEFAULT_IDLE_TIMEOUT = config.threadpool.idle_timeout
DEFAULT_SHUTDOWN_TIMEOUT = config.threadpool.shutdown_timeout


class ThreadPoolExecutor(object):
    def __init__(
        self,
        max_workers: int,
        idle_timeout: int = DEFAULT_IDLE_TIMEOUT,
        shutdown_timeout: int = DEFAULT_SHUTDOWN_TIMEOUT,
        name: Optional[str] = None,
    ) -> None:
        self.max_workers = max_workers
        self.threads: Set[threading.Thread] = set()
        self.mutex = threading.Lock()
        self.queue: deque = deque()
        self.to_shutdown = False
        self.idle_timeout = idle_timeout or None
        self.shutdown_timeout = shutdown_timeout or None
        self.submitted_tasks = 0
        self.worker_id = itertools.count()
        self.name = name or "threadpool"
        self.done_event = None
        self.done_future = None
        self.started = perf_counter()
        self.waiters: List[_thread.LockType] = []
        if config.thread_stack_size:
            threading.stack_size(config.thread_stack_size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.to_shutdown:
            if exc_type:
                # Stop workers and raise error
                self._stop_all_workers()
            else:
                # Graceful shutdown
                self.shutdown(sync=True)

    def _put(self, item):
        with self.mutex:
            if not len(self.waiters) and len(self.threads) < self.max_workers:
                # Start new thread
                name = "worker-%s" % next(self.worker_id)
                t = threading.Thread(target=self.worker, name=name)
                t.daemon = True
                self.threads.add(t)
                t.start()
            # Enqueue task
            self.queue.append(item)
            self.submitted_tasks += 1
            if self.waiters:
                e = self.waiters.pop(0)
                e.release()

    def _get(self, timeout):
        e = None
        endtime = None
        while True:
            with self.mutex:
                if self._qsize():
                    return self.queue.popleft()
                # Waiting lock
                if not e:
                    e = _thread.allocate_lock()
                    e.acquire()
                self.waiters.insert(0, e)
            # Wait for condition or timeout
            t = perf_counter()
            if not endtime:
                endtime = t + timeout
            delay = 0.0005
            while True:
                ready = e.acquire(False)
                if ready:
                    break
                remaining = endtime - t
                if remaining <= 0.0:
                    try:
                        self.waiters.remove(e)
                    except ValueError:
                        pass
                    raise IdleTimeout()
                delay = min(delay * 2, remaining, 0.05)
                time.sleep(delay)
                t = perf_counter()

    def _qsize(self) -> int:
        return len(self.queue)

    def set_max_workers(self, max_workers: int) -> None:
        with self.mutex:
            if max_workers < self.max_workers:
                # Reduce pool
                tl = len(self.threads)
                if tl > max_workers:
                    for i in range(tl - max_workers):
                        self.stop_one_worker()
            self.max_workers = max_workers

    def stop_one_worker(self):
        self._put((None, None, None, None, None, None, None))

    def submit(self, fn: Callable[[], T], *args: Any, **kwargs: Any) -> asyncio.Future[T]:
        if self.to_shutdown:
            raise RuntimeError("Cannot schedule new task after shutdown")
        future: asyncio.Future = asyncio.Future()
        span_ctx, span = get_current_span()
        # Fetch span label
        if "_in_label" in kwargs:
            in_label = kwargs.pop("_in_label")
        else:
            in_label = None
        # Put to the working queue
        self._put((future, fn, args, kwargs, span_ctx, span, in_label))
        return future

    def _stop_all_workers(self):
        for _ in range(len(self.threads)):
            self.stop_one_worker()

    def shutdown(self, sync=False):
        logger.info("Shutdown")
        with self.mutex:
            self.done_future = asyncio.Future()
            if sync:
                self.done_event = threading.Event()
            self.to_shutdown = True
        self._stop_all_workers()
        logger.info("Waiting for workers")
        if sync:
            self.done_event.wait(timeout=self.shutdown_timeout)
            return self.done_future
        else:
            return asyncio.ensure_future(asyncio.wait_for(self.done_future, self.shutdown_timeout))

    @staticmethod
    def _set_future_result(future: asyncio.Future, result: Any) -> None:
        future.get_loop().call_soon_threadsafe(future.set_result, result)

    @staticmethod
    def _set_future_exception(future: asyncio.Future, exc: BaseException) -> None:
        future.get_loop().call_soon_threadsafe(future.set_exception, exc)

    def worker(self):
        t = threading.current_thread()
        logger.debug("Starting worker thread %s", t.name)
        try:
            while not self.to_shutdown:
                try:
                    future, fn, args, kwargs, span_ctx, span, in_label = self._get(
                        self.idle_timeout
                    )
                except IdleTimeout:
                    logger.debug("Closing idle thread")
                    break
                if not future:
                    logger.debug("Worker %s has no future. Stopping", t.name)
                    break
                # if not future.set_running_or_notify_cancel():
                #     continue
                sample = 1 if span_ctx else 0
                if config.features.forensic:
                    if in_label and callable(in_label):
                        in_label = in_label(*args, **kwargs)
                    in_label = in_label or str(fn)
                else:
                    in_label = None
                with Span(
                    service="threadpool",
                    sample=sample,
                    context=span_ctx,
                    parent=span,
                    in_label=in_label,
                ) as span:
                    try:
                        result = fn(*args, **kwargs)
                        self._set_future_result(future, result)
                        result = None  # Release memory
                    except NOCError as e:
                        self._set_future_exception(future, e)
                        span.set_error_from_exc(e, e.default_code)
                        e = None  # Release memory
                    except BaseException as e:
                        self._set_future_exception(future, e)
                        span.set_error_from_exc(e)
                        e = None  # Release memory
        finally:
            logger.debug("Stopping worker thread %s", t.name)
            with self.mutex:
                self.threads.remove(t)
                if self.to_shutdown and not len(self.threads):
                    logger.info("ThreadPool terminated")
                    if self.done_event:
                        self.done_event.set()
                    if self.done_future:
                        self.done_future.set_result(True)

    def may_submit(self):
        """
        Returns true when it possible to submit job
        without overflowing thread limits
        :return:
        """
        with self.mutex:
            return not self.to_shutdown and (
                (self._qsize() < len(self.waiters)) or (self.max_workers > len(self.threads))
            )

    def get_free_workers(self):
        """
        Returns amount of available workers for non-blocking submit
        :return:
        """
        with self.mutex:
            if self.to_shutdown:
                return 0
            return max(
                (self.max_workers - len(self.threads) - self._qsize() + len(self.waiters)), 0
            )

    def apply_metrics(self, d: Dict[str, Any]) -> None:
        """
        Append threadpool metrics to dictionary d
        :param d:
        :return:
        """
        with self.mutex:
            workers = len(self.threads)
            idle = len(self.waiters)
            d.update(
                {
                    "%s_max_workers" % self.name: self.max_workers,
                    "%s_workers" % self.name: workers,
                    "%s_idle_workers" % self.name: idle,
                    "%s_running_workers" % self.name: workers - idle,
                    "%s_submitted_tasks" % self.name: self.submitted_tasks,
                    "%s_queued_jobs" % self.name: len(self.queue),
                    "%s_uptime" % self.name: perf_counter() - self.started,
                }
            )


class IdleTimeout(Exception):
    pass
