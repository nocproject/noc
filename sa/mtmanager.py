# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MapTask Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import threading
import Queue
## Django modules
from django.db import transaction
## NOC modules
from noc.sa.models.maptask import MapTask


logger = logging.getLogger(__name__)


class MTManagerImplementation(object):
    def __init__(self, limit=0):
        self.limit = limit
        self.run_queue = Queue.Queue()
        self.handler_thread = None
        self.handler_lock = threading.Lock()

    def set_limit(self, limit):
        logger.info("Setting MapTask limit to %d", limit)
        self.limit = limit

    def run(self, object, script, params=None, timeout=None):
        """
        Run script and wait for result.
        Returns MapTask instance
        """
        # Check handler thread is ready
        with self.handler_lock:
            if not self.handler_thread or not self.handler_thread.is_alive():
                self.handler_thread = threading.Thread(target=self.handler)
                self.handler_thread.setDaemon(True)
                self.handler_thread.start()
        # Dispose task
        q = Queue.Queue()
        self.run_queue.put((q, object, script, params, timeout))
        # Wait for result
        t = q.get()
        return t

    def handler(self):
        from noc.sa.models.maptask import MapTask
        logger.debug("Start polling")
        tasks = {}  # task id -> queue
        while True:
            # Get all new tasks
            while True:
                try:
                    q, object, script, params, timeout = self.run_queue.get(timeout=1)
                except Queue.Empty:
                    break
                with transaction.commit_on_success():
                    t = MapTask.create_task(object, script, params, timeout)
                if t.status == "F":
                    # Error during creation
                    q.put(t)
                else:
                    tasks[t.id] = q
            if not tasks:
                continue
            # Wait for tasks
            with transaction.commit_on_success():
                for mt in MapTask.objects.filter(
                        status__in=["C", "F"],
                        id__in=list(tasks)):
                    tasks[mt.id].put(mt)
                    del tasks[mt.id]
        logger.debug("Stop")


# Run single instance
MTManager = MTManagerImplementation()
