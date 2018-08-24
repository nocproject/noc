#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# datastream service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import Queue
import time
import random
# Third-party modules
import tornado.gen
import tornado.locks
import tornado.ioloop
import pymongo.errors
# NOC modules
from noc.core.service.base import Service
from noc.services.datastream.handler import DataStreamRequestHandler
from noc.core.datastream.loader import loader
from noc.config import config


class DataStreamService(Service):
    name = "datastream"
    if config.features.traefik:
        traefik_backend = "datastream"
        traefik_frontend_rule = "PathPrefix:/api/datastream"

    def __init__(self):
        super(DataStreamService, self).__init__()
        self.ds_queue = {}

    def get_datastreams(self):
        r = []
        for name in loader.iter_datastreams():
            if not getattr(config.datastream, "enable_%s" % name, False):
                continue
            ds = loader.get_datastream(name)
            if ds:
                self.logger.info("[%s] Initializing datastream", name)
                r += [ds]
            else:
                self.logger.info("[%s] Failed to initialize datastream", name)
        return r

    def get_handlers(self):
        return [
            (
                r"/api/datastream/%s" % ds.name, DataStreamRequestHandler, {
                    "service": self,
                    "datastream": ds
                }
            ) for ds in self.get_datastreams()
        ]

    @tornado.gen.coroutine
    def on_activate(self):
        # Detect we have working .watch() implementation
        if self.has_watch():
            waiter = self.watch_waiter
        else:
            self.logger.warning(
                "Realtime change tracking is not available, using polling emulation."
            )
            waiter = self.sleep_waiter
        # Start watcher threads
        self.ds_queue = {}
        for ds in self.get_datastreams():
            self.logger.info("Starting %s waiter thread", ds.name)
            queue = Queue.Queue()
            self.ds_queue[ds.name] = queue
            thread = threading.Thread(
                target=waiter, args=(ds.get_collection(), queue), name="waiter-%s" % ds.name
            )
            thread.setDaemon(True)
            thread.start()

    def has_watch(self):
        """
        Detect cluster has working .watch() implementation

        :return: True if .watch() is working
        """
        # Get one datastream collection
        dsn = next(loader.iter_datastreams())
        ds = loader.get_datastream(dsn)
        coll = ds.get_collection()
        # Check pymongo has .watch
        if not hasattr(coll, "watch"):
            self.logger.error("pymongo does not support .watch() method")
            return False
        # Check connection is member of replica set
        if not config.mongo.rs:
            self.logger.error("MongoDB must be in replica set mode to use .watch()")
            return False
        # Check version, MongoDB 3.6.0 or later required
        client = coll.database.client
        sv = tuple(int(x) for x in client.server_info()["version"].split("."))
        if sv < (3, 6, 0):
            self.logger.error("MongoDB 3.6 or later require to use .watch()")
            return False
        return True

    def _run_callbacks(self, queue):
        """
        Execute callbacks from queue
        :param queue:
        :return:
        """
        while True:
            try:
                cb = queue.get(block=False)
            except Queue.Empty:
                break
            cb()

    def watch_waiter(self, coll, queue):
        """
        Waiter thread tracking mongo's ChangeStream
        :param coll:
        :param queue:
        :return:
        """
        while True:
            with coll.watch(pipeline=[{"$project": {"_id": 1}}]) as stream:
                try:
                    for _ in stream:
                        # Change received, call all pending callback
                        self._run_callbacks(queue)
                except pymongo.errors.PyMongoError as e:
                    self.logger.error("Unrecoverable watch error: %s", e)
                    time.sleep(1)

    def sleep_waiter(self, coll, queue):
        """
        Simple timeout waiter
        :param coll:
        :param queue:
        :return:
        """
        TIMEOUT = 60
        JITER = 0.1
        while True:
            # Sleep timeout is random of [TIMEOUT - TIMEOUT * JITTER, TIMEOUT + TIMEOUT * JITTER]
            time.sleep(TIMEOUT + (random.random() - 0.5) * TIMEOUT * 2 * JITER)
            self._run_callbacks(queue)

    @tornado.gen.coroutine
    def wait(self, ds_name):
        def notify():
            ioloop.add_callback(event.set)

        if ds_name not in self.ds_queue:
            raise tornado.gen.Return()
        event = tornado.locks.Event()
        ioloop = tornado.ioloop.IOLoop.current()
        self.ds_queue[ds_name].put(notify)
        yield event.wait()


if __name__ == "__main__":
    DataStreamService().start()
