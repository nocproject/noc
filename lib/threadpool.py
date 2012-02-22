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
from threading import Thread, Lock
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
        self.to_shutdown = False
        self.title = "Starting"
        self.start_time = 0
        self.cancelled = False
        self.can_cancel = False

    def run(self):
        while not self.to_shutdown:
            # Get task from queue
            try:
                title, f, args, kwargs = self.queue.get(block=True, timeout=1)
            except Empty:
                continue
            # Run job
            self.pool.change_worker_status(self, True)
            self.title = title
            self.start_time = time.time()
            try:
                self.can_cancel = True
                r = f(*args, **kwargs)
                self.can_cancel = False
            except:
                self.can_cancel = False
                if not self.cancelled:
                    error_report()
            if not self.to_shutdown:
                self.pool.change_worker_status(self, False)
        self.pool.on_worker_complete(self)

    def shutdown(self):
        self.to_shutdown = True

    def cancel(self):
        """
        Forcefully kill thread
        :return:
        """
        self.shutdown()
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
                 min_spare=1, max_spare=1, backlog=1):
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
        self.backlog = backlog
        self.t_lock = Lock()
        self.idle_threads = set()
        self.active_threads = set()
        self.stopping_threads = set()
        self.queue = Queue(backlog)
        self.stopping = False
        self.reschedule_threads()

    def reschedule_threads(self):
        start = []
        stop = []
        with self.t_lock:
            # Run additional threads if below min_spare
            while (not self.stopping and
                   (len(self.idle_threads) +
                    len(self.active_threads) +
                    len(self.stopping_threads) < self.max_threads) and
                   len(self.idle_threads) < self.min_spare):
                w = Worker(self, self.queue)
                self.idle_threads.add(w)
                start += [w]
            # Stop excessive threads
            while len(self.idle_threads) > self.max_spare:
                w = self.idle_threads.pop()
                self.stopping_threads.add(w)
                stop += [w]
        # Shutdown threads
        for w in stop:
            w.shutdown()
        # Run threads
        for w in start:
            w.start()

    def change_worker_status(self, worker, status):
        """
        :param worker:
        :param status:
        :return:
        """
        with self.t_lock:
            if status:
                # Worker became active
                self.idle_threads.remove(worker)
                self.active_threads.add(worker)
            else:
                # Worker became idle
                self.active_threads.remove(worker)
                self.idle_threads.add(worker)
        self.reschedule_threads()

    def on_worker_complete(self, worker):
        """
        :param worker:
        :return:
        """
        with self.t_lock:
            if worker in self.idle_threads:
                self.idle_threads.remove(worker)
            if worker in self.active_threads:
                self.active_threads.remove(worker)
            if worker in self.stopping_threads:
                self.stopping_threads.remove(worker)
        self.reschedule_threads()

    def get_status(self):
        s = []
        t = time.time()
        with self.t_lock:
            for w in self.active_threads:
                s += [{
                    "id": w.ident,
                    "status": "ACTIVE",
                    "title": w.title,
                    "start": w.start_time,
                    "duration": t - w.start_time
                }]
            for w in self.idle_threads:
                s += [{
                    "id": w.ident,
                    "status": "IDLE"
                }]
            for w in self.stopping_threads:
                s += [{
                    "id": w.ident,
                    "status": "STOP"
                }]
        return s

    def stop(self, timeout=None):
        with self.t_lock:
            self.stopping = True
            for w in self.idle_threads:
                w.shutdown()
            for w in self.active_threads:
                w.shutdown()
            self.stopping_threads |= self.idle_threads
            self.stopping_threads |= self.active_threads
            self.stopping_threads = set()
            self.active_threads = set()
        # Wait for completion
        t0 = time.time()
        while self.stopping_threads:
            time.sleep(1)
            if self.timeout is not None and time.time() - t0 > timeout:
                break
        # Cancel forcefully
        for i in range(3):
            with self.t_lock:
                if not self.stopping_threads:
                    break
                for w in self.stopping_threads:
                    w.cancel()
            time.sleep(3)

    def run(self, title, target, args=(), kwargs={}):
        # Block, timeout
        self.queue.put((title, target, args, kwargs))


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
