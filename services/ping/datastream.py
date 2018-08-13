# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Ping DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class PingDataStreamClient(DataStreamClient):
    def on_change(self, data):
        self.service.update_probe(data)

    def on_delete(self, data):
        self.service.delete_probe(data["id"])
