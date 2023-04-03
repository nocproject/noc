# ----------------------------------------------------------------------
# Topo DataStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, List

# NOC modules
from noc.core.datastream.client import DataStreamClient
from .types import ObjectSnapshot


class TopoDataStreamClient(DataStreamClient):
    async def on_change(self, data: Dict[str, Any]):
        links: List[int] = []
        uplinks: List[int] = []
        for iface in data.get("interfaces", []):
            for link in iface.get("link", []):
                links.append(int(link["object"]))
                if link.get("is_uplink"):
                    uplinks.append(int(link["object"]))
        snapshot = ObjectSnapshot(
            id=int(data["id"]),
            level=data["object_profile"]["level"],
            links=links or None,
            uplinks=uplinks or None,
        )
        self.service.topo.sync_object(snapshot)

    async def on_delete(self, data):
        await self.service.on_delete(int(data["id"]))

    async def on_ready(self):
        await self.service.set_ready()
