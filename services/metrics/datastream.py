# ----------------------------------------------------------------------
# Metrics DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class MetricsDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_source_config(data)

    async def on_delete(self, data):
        await self.service.delete_source_config(int(data["id"]))

    async def on_ready(self):
        await self.service.on_mappings_ready()


class MetricRulesDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_rules(data)

    async def on_delete(self, data):
        await self.service.delete_rules(data["id"])

    async def on_ready(self):
        await self.service.on_rules_ready()
