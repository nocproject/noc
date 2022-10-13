# ----------------------------------------------------------------------
# cfgmxroute
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# NOC modules
from noc.core.datastream.base import DataStream
from noc.main.models.messageroute import MessageRoute


class CfgMetricsCollectorDataStream(DataStream):
    name = "cfgmxroute"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        route: "MessageRoute" = MessageRoute.objects.get(id=oid)
        if not route or not route.is_active:
            raise KeyError()
        r = route.get_route_config()
        r["id"] = str(route.id)
        return r
