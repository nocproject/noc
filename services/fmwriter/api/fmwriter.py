# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## FMWriter API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.service.api.base import ServiceAPI, api


class FMWriterAPI(ServiceAPI):
    """
    Monitoring API
    """
    name = "fmwriter"
    level = ServiceAPI.AL_POOL

    @api
    def event(self, timestamp, managed_object, data):
        """
        Register FM event
        :param timestamp: Event timestamp (Unix timestamp)
        :param managed_object: Managed object id
        :param data: Event data as dict
        """
        self.service.spool_event(
            datetime.datetime.fromtimestamp(timestamp),
            managed_object,
            data
        )

    @api
    def events(self, data):
        """
        Register batch of events
        data is a list of
            - timestamp
            - managed_object
            - event raw data
        """
        for e in data:
            self.service.spool_event(
                datetime.datetime.fromtimestamp(e["ts"]),
                e["object"],
                e["data"]
            )
