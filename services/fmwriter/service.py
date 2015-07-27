#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Node Manager service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import itertools
import struct
import time
# Third-party modules
from bson import Binary
import tornado.ioloop
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter
from noc.fm.models.newevent import NewEvent
from api.fmwriter import FMWriterAPI


class FMWriterService(Service):
    name = "fmwriter"

    #
    leader_group_name = "fmwriter-%(env)s-%(pool)s"
    pooled = True
    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }

    api = Service.api + [
        FMWriterAPI
    ]

    def __init__(self):
        super(FMWriterService, self).__init__()
        self.event_batch = None
        self.batched_events = 0
        self.event_seq = itertools.count()
        self.event_batch = None
        self.batched_events = 0
        self.write_batch_callback = None

    def spool_event(self, timestamp, managed_object, data):
        # Normalize data
        data = dict(
            (str(k).replace(".", "__").replace("$", "^^"), str(data[k]))
            for k in data
        )
        # Generate sequental number
        seq = Binary(struct.pack(
            "!II",
            int(time.time()),
            self.event_seq.next() & 0xFFFFFFFFL
        ))
        # Batch event
        if not self.event_batch:
            self.event_batch = NewEvent._get_collection().initialize_ordered_bulk_op()
        self.event_batch.insert({
            "timestamp": timestamp,
            "managed_object": managed_object,
            "raw_vars": data,
            "log": [],
            "seq": seq
        })
        self.batched_events += 1

    def write_batch(self):
        if self.event_batch and self.batched_events:
            self.logger.debug("Writing %d batched events",
                              self.batched_events)
            self.event_batch.execute()
            # Destroy batch
            self.event_batch = None
            self.batched_events = 0

    def on_activate(self):
        self.write_batch_callback = tornado.ioloop.PeriodicCallback(
            self.write_batch,
            1000,
            self.ioloop
        )
        self.write_batch_callback.start()


if __name__ == "__main__":
    FMWriterService().start()
