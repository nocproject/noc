# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Trap DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class TrapDataStreamClient(DataStreamClient):
    def on_change(self, data):
        self.service.update_source(data)

    def on_delete(self, data):
        self.service.delete_source(data["id"])
