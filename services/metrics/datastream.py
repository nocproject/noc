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
        self.service.update_mapping(
            mo_id=int(data["id"]),
            bi_id=int(data["bi_id"]),
            fm_pool=data["fm_pool"],
            labels=data.get("labels") or [],
            metric_labels=data.get("metric_labels") or [],
        )

    async def on_delete(self, data):
        self.service.delete_mapping(int(data["id"]))

    async def on_ready(self):
        await self.service.on_mappings_ready()
