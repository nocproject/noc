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

    def __init__(self):
        super(ProbeDaemon, self).__init__()
        self.tasks = {}  # uuid -> Task
        self.pending_queue = []
        self.running = set()  # UUID
        self.pending_lock = Lock()
        self.thread_pool = None
        self.sender = None
        self.io = None

    def run(self):
        # Run sender thread
        self.sender = Sender(self)
        self.sender.start()
        self.io = IOThread(self)
        self.io.start()
        # Prepare thread pool
        self.thread_pool = Pool(
            start_threads=self.config.getint("thread_pool", "start_threads"),
            min_spare=self.config.getint("thread_pool", "min_spare"),
            max_spare=self.config.getint("thread_pool", "max_spare"),
            max_threads=self.config.getint("thread_pool", "max_threads"),
            backlog=self.config.getint("thread_pool", "backlog")
        )
        while True:
            t = time.time()
            with self.pending_lock:
                while self.pending_queue and self.pending_queue[0].next_run < t:
                    rt = self.pending_queue.pop(0)
                    self.running.add(rt.uuid)
                    self.thread_pool.run(repr(rt), rt.run)
            st = 1 if not self.pending_queue else self.pending_queue[0].next_run - t
            time.sleep(min(st, 1))

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
