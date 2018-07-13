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
# Third-party modules
import tornado.gen
import tornado.locks
import tornado.ioloop
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

    def get_datastreams(self):
        r = []
        for name in loader.iter_datastreams():
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
        self.ds_queue = {}
        for ds in self.get_datastreams():
            try:
                ds.get_collection().watch()
            except TypeError:
                self.logger.warning("MongoDB less than version 3.6 not support watch.")
                break
            self.logger.info("Starting %s waiter thread", ds.name)
            queue = Queue.Queue()
            self.ds_queue[ds.name] = queue
            thread = threading.Thread(
                target=self.waiter, args=(ds.get_collection(), queue), name="waiter-%s" % ds.name
            )
            thread.setDaemon(True)
            thread.start()

    def waiter(self, coll, queue):
        with coll.watch() as stream:
            for _ in stream:
                # Change received, call all pending callback
                while True:
                    try:
                        cb = queue.get(block=False)
                    except Queue.Empty:
                        break  # No pending callbacks
                    cb()

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
