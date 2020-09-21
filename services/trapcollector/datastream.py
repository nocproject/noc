# ----------------------------------------------------------------------
# Trap DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class TrapDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_source(data)

    async def on_delete(self, data):
        await self.service.delete_source(data["id"])
