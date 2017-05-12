# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ThreadPool class
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import Queue
import threading
import logging
import itertools
## Third-party modules
from concurrent.futures import Future
from atomiclong import AtomicLong

logger = logging.getLogger(__name__)

DEFAULT_IDLE_TIMEOUT = 300
DEFAULT_SHUTDOWN_TIMEOUT = 60


class ThreadPoolExecutor(object):
    def __init__(self, max_workers, idle_timeout=DEFAULT_IDLE_TIMEOUT,
                 shutdown_timeout=DEFAULT_SHUTDOWN_TIMEOUT,
                 name=None):
        self.max_workers = max_workers
        self.threads = set()
        self.threads_lock = threading.Lock()
        self.queue = Queue.Queue()
        self.to_shutdown = False
        self.idle_timeout = idle_timeout or None
        self.shutdown_timeout = shutdown_timeout or None
        self.idle_workers = AtomicLong(0)
        self.worker_id = itertools.count()
        self.name = name or "threadpool"
        self.done_event = threading.Event()

    def set_max_workers(self, max_workers):
        with self.threads_lock:
            if max_workers < self.max_workers:
                # Reduce pool
                l = len(self.threads)
                if l > max_workers:
                    for i in range(l - max_workers):
                        self.stop_one_worker()
            self.max_workers = max_workers

    def stop_one_worker(self):
        self.queue.put((None, None, None, None))

    def submit(self, fn, *args, **kwargs):
        if self.to_shutdown:
            raise RuntimeError(
                "Cannot schedule new task after shutdown")
        future = Future()
        self.queue.put((future, fn, args, kwargs))
        self.adjust_workers()
        return future

    def adjust_workers(self):
        with self.threads_lock:
            while (self.queue.qsize() > self.idle_workers.value and
                    len(self.threads) < self.max_workers):
                name = "worker-%s" % self.worker_id.next()
                t = threading.Thread(target=self.worker, name=name)
                t.setDaemon(True)
                self.threads.add(t)
                self.idle_workers += 1
                t.start()

    def shutdown(self):
        logging.info("Shutdown")
        with self.threads_lock:
            self.to_shutdown = True
        for _ in self.threads:
            self.stop_one_worker()
        logging.info("Waiting for workers")
        self.done_event.wait(timeout=self.shutdown_timeout)
        logging.info("ThreadPool terminated")

    def worker(self):
        t = threading.current_thread()
        logger.debug("Starting worker thread %s", t.name)
        self.idle_workers -= 1
        try:
            while not self.to_shutdown:
                try:
                    self.idle_workers += 1
                    future, fn, args, kwargs = self.queue.get(
                        block=True,
                        timeout=self.idle_timeout
                    )
                except Queue.Empty:
                    logger.debug("Closing idle thread")
                    break
                finally:
                    self.idle_workers -= 1
                if not future:
                    logging.debug("Worker %s has no future. Stopping",
                                  t.name)
                    break
                if not future.set_running_or_notify_cancel():
                    continue
                try:
                    result = fn(*args, **kwargs)
                except BaseException as e:
                    future.set_exception(e)
                else:
                    future.set_result(result)
        finally:
            logger.debug("Stopping worker thread %s", t.name)
            with self.threads_lock:
                self.threads.remove(t)
                if self.to_shutdown and not len(self.threads):
                    self.done_event.set()

    def may_submit(self):
        """
        Returns true when it possible to submit job
        without overflowing thread limits
        :return: 
        """
        with self.threads_lock:
            return ((self.queue.qsize() < self.idle_workers.value)
                    or (self.max_workers > len(self.threads)))

    def get_free_workers(self):
        """
        Returns amount of available workers for non-blocking submit
        :return: 
        """
        with self.threads_lock:
            return (self.max_workers -
                    len(self.threads) -
                    self.queue.qsize() +
                    self.idle_workers.value)

    def apply_metrics(self, d):
        """
        Append threadpool metrics to dictionary d
        :param d: 
        :return: 
        """
        with self.threads_lock:
            workers = len(self.threads)
            idle = self.idle_workers.value
            d.update({
                "%s_max_workers": self.max_workers,
                "%s_workers": workers,
                "%s_idle_workers": idle,
                "%s_running_workers": workers - idle
            })
