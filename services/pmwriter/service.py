#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PM Writer service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
# Third-party modules
import tornado.ioloop
## NOC modules
from noc.core.service.base import Service
from noc.sa.interfaces.base import StringParameter, IntParameter
from api.pmwriter import PMWriterAPI
from noc.pm.db.base import tsdb


class PMWriterService(Service):
    name = "pmwriter"

    #
    leader_group_name = "pmwriter"
    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        ),
        "batch_size": IntParameter(default=1000)
    }

    api = Service.api + [
        PMWriterAPI
    ]

    def __init__(self):
        super(PMWriterService, self).__init__()
        self.batch = tsdb.get_batch()
        self.batched_metrics = 0
        self.flush_callback = None

    def spool_metric(self, metric, timestamp, value):
        """
        Spool metric value to batch
        """
        self.logger.debug("Register metric %s %s %s",
                          metric, value, timestamp)
        self.batch.write(metric, timestamp, value)
        self.batched_metrics += 1
        if self.batched_metrics >= self.config.batch_size:
            self.flush()

    def flush(self):
        """
        Write batch to database
        """
        if not self.batched_metrics:
            return
        t0 = self.ioloop.time()
        self.batch.flush()
        dt =self.ioloop.time() - t0
        self.logger.debug(
            "%d metrics flushed (%.2fms)",
            self.batched_metrics, dt
        )
        self.batch = tsdb.get_batch()
        self.batched_metrics = 0

    def on_activate(self):
        self.flush_callback = tornado.ioloop.PeriodicCallback(
            self.flush,
            1000,
            self.ioloop
        )
        self.flush_callback.start()


if __name__ == "__main__":
    PMWriterService().start()
