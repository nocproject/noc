# ----------------------------------------------------------------------
# EventRule DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class EventRuleDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_rule(data)

    async def on_delete(self, data):
        await self.service.delete_rule(data["id"])

    async def on_ready(self):
        await self.service.on_event_rules_ready()


class EventConfigDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_config(data)

    async def on_delete(self, data):
        await self.service.delete_config(data["id"])

    async def on_ready(self):
        await self.service.on_event_config_ready()
