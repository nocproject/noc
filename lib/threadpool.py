# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Thread Pool abstraction
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
from Queue import Queue, Empty
from threading import Thread, Lock, Event
import time
import ctypes
## NOC modules
from noc.lib.debug import error_report


class CancelledError(Exception):
    pass


class Worker(Thread):
    def __init__(self, pool, queue, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.pool = pool
        self.queue = queue
        self.title = "Starting"
        self.start_time = 0
        self.cancelled = False
        self.can_cancel = False
        self.is_idle = True

    def run(self):
        while True:
            # Get task from queue
            try:
                task = self.queue.get(block=True, timeout=1)
            except Empty:
                continue
            if task is None:
                break  # Shutdown
            title, f, args, kwargs = task
            # Run job
            self.title = title
            self.start_time = time.time()
            try:
                self.can_cancel = True
                self.is_idle = False
                f(*args, **kwargs)
                self.can_cancel = False
            except CancelledError:
                break
            except:
                self.can_cancel = False
                if not self.cancelled:
                    error_report()
            self.queue.task_done()
            self.is_idle = True
        # Shutdown
        self.queue.task_done()
        self.pool.thread_done(self)

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
    def __init__(self, start_threads=1, max_threads=10,
                 min_spare=1, max_spare=1, backlog=0):
        if min_spare > max_spare:
            raise ValueError("min_spare (%d) must not be greater"
                             " than max_spare (%d)" % (min_spare,
                                                       max_spare))
        if start_threads > max_threads:
            raise ValueError("start_threads (%d) must not be greater"
                             " than max_threads (%d)" % (start_threads,
                                                         max_threads))
        self.start_threads = start_threads
        self.max_threads = max_threads
        self.min_spare = min_spare
        self.max_spare = max_spare
        self.backlog = backlog if backlog else max_threads
        self.t_lock = Lock()
        self.threads = set()
        self.queue = Queue(backlog)
        self.stopping = False
        self.stopped = Event()
        self.reschedule_threads()

    def reschedule_threads(self):
        if self.stopping:
            return
        with self.t_lock:
            # Idle threads
            n_idle = sum(1 for t in self.threads
                         if t.is_alive() and t.is_idle)
            # Total threads
            n = len(self.threads)
            # Run spare threads
            while n_idle < self.min_spare and n < self.max_threads:
                w = Worker(self, self.queue)
                self.threads.add(w)
                n_idle += 1
                n += 1
                w.start()
            # Shutdown spare threads
            while n_idle > self.max_spare:
                self.queue.put(None)
                n_idle -= 1
                n -= 1

    def thread_done(self, t):
        with self.t_lock:
            if t in self.threads:
                self.threads.remove(t)
            if self.stopping and not len(self.threads):
                self.stopped.set()
        self.reschedule_threads()

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
        # @todo: Limit rescheduling
        self.reschedule_threads()
        # Block, timeout
        self.queue.put((title, target, args, kwargs))

    def configure(self, max_threads=None, min_spare=None,
                  max_spare=None, backlog=None):
        if max_threads is not None:
            self.max_threads = max_threads
        if min_spare is not None:
            self.min_spare = min_spare
        if max_spare is not None:
            self.max_spare = max_spare
        if backlog is not None:
            self.backlog = backlog


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
