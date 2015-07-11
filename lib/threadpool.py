# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Thread Pool abstraction
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from Queue import Queue, Empty
from threading import Thread, Lock, Event
import time
import ctypes
import logging
## NOC modules
from noc.lib.debug import error_report
from noc.lib.log import PrefixLoggerAdapter
from noc.lib.perf import MetricsHub

logger = logging.getLogger(__name__)


class CancelledError(Exception):
    pass


class Worker(Thread):
    def __init__(self, pool, queue, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.setDaemon(True)
        self.pool = pool
        self.queue = queue
        self.logger = self.pool.logger
        self.title = "Starting"
        self.start_time = 0
        self.cancelled = False
        self.can_cancel = False
        self.is_idle = False

    def set_idle(self, status):
        self.is_idle = status
        if status:
            self.title = "idle"
        self.pool.set_idle(status)

    def get_task(self):
        self.set_idle(True)
        while True:
            try:
                task = self.queue.get(block=True, timeout=1)
                self.set_idle(False)
                return task
            except Empty:
                # Apply pool scheduling
                self.set_idle(True)

    def run(self):
        self.logger.debug("Starting worker thread")
        while True:
            # Get task from queue
            task = self.get_task()
            if task is None:
                break  # Shutdown
            title, f, args, kwargs = task
            # Run job
            self.title = title
            self.start_time = time.time()
            try:
                self.can_cancel = True
                f(*args, **kwargs)
                self.can_cancel = False
            except CancelledError:
                break
            except:
                self.can_cancel = False
                if not self.cancelled:
                    error_report()
            self.queue.task_done()
            self.logger.debug("[%s] complete in %ss",
                              title, time.time() - self.start_time)
            self.start_time = 0
        # Shutdown
        self.queue.task_done()
        self.pool.thread_done(self)
        self.logger.debug("Stopping worker thread")

    def cancel(self):
        """
        Forcefully kill thread
        :return:
        """
        self.cancelled = True
        if not self.isAlive():
            return  # Already dead
        if not self._thread_id:
            return  # No thread id
        if not self.can_cancel:
            return  # No cancellable part
        r = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self._thread_id),
            ctypes.py_object(CancelledError))
        if r > 1:
            # Failed to raise exception
            # Revert back thread state
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.ident), None)


class Pool(object):
    def __init__(self, name="pool", metrics_prefix=None,
                 start_threads=1, max_threads=10,
                 min_spare=1, max_spare=1, backlog=0):
        max_threads = max_threads or 100
        if min_spare > max_spare:
            raise ValueError("min_spare (%d) must not be greater"
                             " than max_spare (%d)" % (min_spare,
                                                       max_spare))
        if start_threads > max_threads:
            raise ValueError("start_threads (%d) must not be greater"
                             " than max_threads (%d)" % (start_threads,
                                                         max_threads))
        self.logger = PrefixLoggerAdapter(logger, name)
        self.name = name
        if not metrics_prefix:
            metrics_prefix = "noc"
        metrics_prefix += "pool.%s" % name
        self.metrics = MetricsHub(
            metrics_prefix,
            "threads.running",
            "threads.idle",
            "queue.len"
        )
        self.start_threads = start_threads
        self.max_threads = max_threads
        self.min_spare = min_spare
        self.max_spare = max_spare
        self.backlog = backlog or max_threads
        self.t_lock = Lock()
        self.threads = set()
        self.queue = Queue(backlog)
        self.stopping = False
        self.stopped = Event()
        self.n_idle = 0
        self.idle_lock = Lock()
        self.logger.info("Running thread pool '%s'", self.name)
        self.set_idle(None)

    def set_idle(self, status):
        with self.idle_lock:
            if status is not None:
                self.n_idle += 1 if status else -1
            n = len(self.threads)
            self.metrics.threads_idle = self.n_idle
            self.metrics.threads_running = n
            self.metrics.queue_len = self.queue.qsize()
            if (not status and self.n_idle < self.min_spare and
                        n < self.max_threads):
                # Run additional thread
                w = Worker(self, self.queue)
                self.threads.add(w)
                w.start()
            elif status and (self.n_idle > self.max_spare or n > self.max_threads):
                # Stop one thread
                self.queue.put(None)

    def thread_done(self, t):
        with self.t_lock:
            if t in self.threads:
                self.threads.remove(t)
            if self.stopping and not len(self.threads):
                self.stopped.set()

    def get_status(self):
        s = []
        t = time.time()
        with self.t_lock:
            for w in self.threads:
                if w.is_idle:
                    s += [{
                        "id": w.ident,
                        "status": "IDLE"
                    }]
                else:
                    s += [{
                        "id": w.ident,
                        "status": "RUN",
                        "title": w.title,
                        "start": w.start_time,
                        "duration": t - w.start_time
                    }]
        return s

    def stop(self, timeout=3):
        self.stopping = True
        with self.t_lock:
            n = len(self.threads)
            if not n:
                return  # Stopped
            for i in range(n):
                self.queue.put(None)  # Send shutdown signals
        # Wait for clean stop
        self.stopped.wait(timeout)
        if self.stopped.is_set():
            return
        # Forcefully cancel
        with self.t_lock:
            for t in self.threads:
                if t.is_alive():
                    t.cancel()
        time.sleep(timeout)

    def run(self, title, target, args=(), kwargs={}):
        if self.stopping:
            return
        self.queue.put((title, target, args, kwargs))

    def configure(self, max_threads=None, min_spare=None,
                  max_spare=None, backlog=None):
        if max_threads is not None:
            self.max_threads = max_threads
            if not backlog:
                backlog = max_threads
        if min_spare is not None:
            self.min_spare = min_spare
        if max_spare is not None:
            self.max_spare = max_spare
        else:
            self.max_spare = max(self.max_threads // 4, 1)
        if backlog is not None:
            self.backlog = backlog
            self.queue.maxsize = backlog
        self.log_config()

    def is_blocked(self):
        return self.queue.qsize() >= self.backlog

    def log_config(self):
        logger.debug(
            "Pool settings: name=%s start_threads=%s max_threads=%s "
            "min_spare=%s max_spare=%s backlog=%s",
            self.name, self.start_threads, self.max_threads,
            self.min_spare, self.max_spare, self.backlog
        )


class LabeledPool(object):
    def __init__(self, config):
        # Run pools
        self.labels = {}  # Label -> Pool
        for cfg in config:
            label = cfg["label"]
            args = {}
            for a in ("start_threads", "max_threads", "min_spare",
                      "max_spare", "backlog"):
                if a in cfg:
                    args[a] = cfg[a]
            self.labels[label] = Pool(**args)

    def run(self, label, title, target, args, kwargs):
        if label not in self.labels:
            label = None
        self.labels[label].run(title, target, args, kwargs)

    def stop(self):
        for pool in self.labels.values():
            pool.stop()  # @todo: Parallel stopping
