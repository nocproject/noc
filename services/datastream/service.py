#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# datastream service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import Service
from noc.services.datastream.handler import DataStreamRequestHandler
from noc.services.datastream.streams.managedobject import ManagedObjectDataStream
from noc.config import config


class DataStreamService(Service):
    name = "datastream"
    if config.features.traefik:
        traefik_backend = "datastream"
        traefik_frontend_rule = "PathPrefix:/api/datastream"

    def get_datastreams(self):
        return [ManagedObjectDataStream]

    def get_handlers(self):
        return [
            (
                r"/api/datastream/%s" % ds.name, DataStreamRequestHandler, {
                    "service": self,
                    "datastream": ds
                }
            ) for ds in self.get_datastreams()
        ]


if __name__ == "__main__":
    DataStreamService().start()
