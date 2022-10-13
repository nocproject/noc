# ----------------------------------------------------------------------
# MX DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class RouteDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_route(data)

    async def on_delete(self, data):
        await self.service.delete_route(data["id"])
