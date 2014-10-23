# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-probe daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import bisect
import logging
from threading import Lock
import Queue
## NOC modules
from noc.lib.daemon.autoconf import AutoConfDaemon
from task import Task
from sender import Sender
from io.base import IOThread
from noc.lib.threadpool import Pool


class ProbeDaemon(AutoConfDaemon):
    daemon_name = "noc-probe"
    AUTOCONF_PATH = "/pm/probe/"
    MAX_SLEEP = 0.5

    def __init__(self):
        super(ProbeDaemon, self).__init__()
        self.tasks = {}  # uuid -> Task
        self.pending_queue = []
        self.running = set()  # UUID
        self.pending_lock = Lock()
        self.thread_pool = None
        self.sender = None
        self.io = None

    def iter_tasks(self):
        """
        Yield task to run
        """
        while True:
            t = time.time()
            while True:
                with self.pending_lock:
                    if (self.pending_queue and
                                self.pending_queue[0].next_run <= t):
                        rt = self.pending_queue.pop(0)
                        self.running.add(rt.uuid)
                    else:
                        # Nothing to run, go sleep
                        if not self.pending_queue:
                            st = self.MAX_SLEEP
                        else:
                            st = min(self.MAX_SLEEP,
                                     self.pending_queue[0].next_run - t)
                        break
                # Yield outside of lock
                yield rt
            time.sleep(st)

    def run(self):
        # Run sender thread
        self.sender = Sender(self)
        self.sender.start()
        self.io = IOThread(self)
        self.io.start()
        # Prepare thread pool
        max_threads = self.config.getint("thread_pool", "max_threads")
        backlog = self.config.getint("thread_pool", "backlog")
        if not backlog:
            backlog = 2 * max_threads
        self.thread_pool = Pool(
            name="probes",
            metrics_prefix=self.metrics,
            start_threads=self.config.getint("thread_pool", "start_threads"),
            min_spare=self.config.getint("thread_pool", "min_spare"),
            max_spare=self.config.getint("thread_pool", "max_spare"),
            max_threads=max_threads,
            backlog=backlog
        )
        for rt in self.iter_tasks():
            self.thread_pool.run(repr(rt), rt.run)

    def on_object_create(self, uuid, **kwargs):
        t = Task(self)
        self.tasks[uuid] = t
        t.configure(uuid=uuid, **kwargs)

    def on_object_delete(self, uuid):
        del self.tasks[uuid]

    def on_object_change(self, uuid, **kwargs):
        self.tasks[uuid].configure(uuid=uuid, **kwargs)

    def reschedule(self, t):
        with self.pending_lock:
            bisect.insort_right(
                self.pending_queue,
                t
            )
        self.sender.flush()
