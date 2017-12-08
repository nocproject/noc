# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ThreadPool class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import thread
import logging
import itertools
import time
import datetime
from collections import deque
import sys
# Third-party modules
from concurrent.futures import Future
from tornado.gen import with_timeout
from noc.config import config
from noc.core.span import Span, get_current_span
from noc.core.error import NOCError, ERR_UNKNOWN

logger = logging.getLogger(__name__)

DEFAULT_IDLE_TIMEOUT = config.threadpool.idle_timeout
DEFAULT_SHUTDOWN_TIMEOUT = config.threadpool.shutdown_timeout


class ThreadPoolExecutor(object):
    def __init__(self, max_workers, idle_timeout=DEFAULT_IDLE_TIMEOUT,
                 shutdown_timeout=DEFAULT_SHUTDOWN_TIMEOUT,
                 name=None):
        self.max_workers = max_workers
        self.threads = set()
        self.mutex = threading.Lock()
        self.queue = deque()
        self.to_shutdown = False
        self.idle_timeout = idle_timeout or None
        self.shutdown_timeout = shutdown_timeout or None
        self.submitted_tasks = 0
        self.worker_id = itertools.count()
        self.name = name or "threadpool"
        self.done_event = None
        self.done_future = None
        self.started = time.time()
        self.waiters = []
        if config.thread_stack_size:
            threading.stack_size(config.thread_stack_size)

    def _put(self, item):
        with self.mutex:
            if not len(self.waiters) and len(self.threads) < self.max_workers:
                # Start new thread
                name = "worker-%s" % next(self.worker_id)
                t = threading.Thread(target=self.worker, name=name)
                t.setDaemon(True)
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
                    e = thread.allocate_lock()
                    e.acquire()
                self.waiters.insert(0, e)
            # Wait for condition or timeout
            t = time.time()
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
                t = time.time()

    def _qsize(self):
        return len(self.queue)

    def set_max_workers(self, max_workers):
        with self.mutex:
            if max_workers < self.max_workers:
                # Reduce pool
                tl = len(self.threads)
                if tl > max_workers:
                    for i in range(tl - max_workers):
                        self.stop_one_worker()
            self.max_workers = max_workers

    def stop_one_worker(self):
        self._put((None, None, None, None, None, None))

    def submit(self, fn, *args, **kwargs):
        if self.to_shutdown:
            raise RuntimeError(
                "Cannot schedule new task after shutdown")
        future = Future()
        span_ctx, span = get_current_span()
        # Fetch span label
        if "_in_label" in kwargs:
            in_label = kwargs.pop("_in_label")
        else:
            in_label = None
        # Put to the working queue
        self._put((future, fn, args, kwargs, span_ctx, span, in_label))
        return future

    def shutdown(self, sync=False):
        logging.info("Shutdown")
        with self.mutex:
            self.done_future = Future()
            if not sync:
                self.done_event = threading.Event()
            self.to_shutdown = True
        for _ in range(len(self.threads)):
            self.stop_one_worker()
        logging.info("Waiting for workers")
        if sync:
            self.done_event.wait(timeout=self.shutdown_timeout)
            return self.done_future
        else:
            return with_timeout(
                timeout=datetime.timedelta(
                    seconds=self.shutdown_timeout),
                future=self.done_future
            )

    def worker(self):
        t = threading.current_thread()
        logger.debug("Starting worker thread %s", t.name)
        try:
            while not self.to_shutdown:
                try:
                    future, fn, args, kwargs, span_ctx, span, in_label = self._get(self.idle_timeout)
                except IdleTimeout:
                    logger.debug("Closing idle thread")
                    break
                if not future:
                    logging.debug("Worker %s has no future. Stopping",
                                  t.name)
                    break
                if not future.set_running_or_notify_cancel():
                    continue
                sample = 1 if span_ctx else 0
                if config.features.forensic:
                    if in_label and callable(in_label):
                        in_label = in_label(*args, **kwargs)
                    in_label = in_label or str(fn)
                else:
                    in_label = None
                with Span(service="threadpool", sample=sample,
                          context=span_ctx, parent=span,
                          in_label=in_label) as span:
                    try:
                        result = fn(*args, **kwargs)
                        future.set_result(result)
                    except NOCError as e:
                        exc_info = sys.exc_info()
                        future.set_exception_info(e, exc_info[2])
                        span.error_code = e.default_code
                        span.error_text = str(e)
                    except BaseException as e:
                        exc_info = sys.exc_info()
                        future.set_exception_info(e, exc_info[2])
                        span.error_code = ERR_UNKNOWN
                        span.error_text = str(e)
        finally:
            logger.debug("Stopping worker thread %s", t.name)
            with self.mutex:
                self.threads.remove(t)
                if self.to_shutdown and not len(self.threads):
                    logging.info("ThreadPool terminated")
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
                (self._qsize() < len(self.waiters)) or
                (self.max_workers > len(self.threads))
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
                (self.max_workers - len(self.threads) -
                 self._qsize() + len(self.waiters)),
                0
            )

    def apply_metrics(self, d):
        """
        Append threadpool metrics to dictionary d
        :param d:
        :return:
        """
        with self.mutex:
            workers = len(self.threads)
            idle = len(self.waiters)
            d.update({
                "%s_max_workers" % self.name: self.max_workers,
                "%s_workers" % self.name: workers,
                "%s_idle_workers" % self.name: idle,
                "%s_running_workers" % self.name: workers - idle,
                "%s_submitted_tasks" % self.name: self.submitted_tasks,
                "%s_queued_jobs" % self.name: len(self.queue),
                "%s_uptime" % self.name: time.time() - self.started
            })


class IdleTimeout(Exception):
    pass
