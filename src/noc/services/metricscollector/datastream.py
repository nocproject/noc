# ----------------------------------------------------------------------
# Metricscollector DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.client import DataStreamClient


class MetricsDataStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_metric_type(data)

    async def on_delete(self, data):
        await self.service.delete_metric_type(data["id"])

    async def on_ready(self):
        await self.service.on_ready()


class SourceStreamClient(DataStreamClient):
    async def on_change(self, data):
        await self.service.update_source(data)

    async def on_delete(self, data):
        await self.service.delete_source(data["id"])

    async def on_ready(self):
        await self.service.on_event_source_ready()
        self.service.logger.info("Initial object mappings are ready")
