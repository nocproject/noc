# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMWriter API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.service.api.base import ServiceAPI, api


class PMWriterAPI(ServiceAPI):
    """
    PM collector api
    """
    name = "pmwriter"
    level = ServiceAPI.AL_GLOBAL

    @api
    def metric(self, metric, timestamp, value):
        """
        Register PM metric
        :param metric: Graphite metric name
        :param timestamp: Unix timestamp
        :param value: Metric value as float
        """
        self.service.spool_metric(metric, timestamp, value)

    @api
    def metrics(self, data):
        """
        Register list of PM metrics
        :param data: List of [metric, timestamp, value]
        """
        for metric, timestamp, value in data:
            self.service.spool_metric(metric, timestamp, value)
