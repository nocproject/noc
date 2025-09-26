# ----------------------------------------------------------------------
# cfgmxroute
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.datastream.base import DataStream
from noc.main.models.messageroute import MessageRoute
from noc.main.models.notificationgroup import NotificationGroup


class CfgMetricsCollectorDataStream(DataStream):
    name = "cfgmxroute"

    @classmethod
    def get_object(cls, oid: str) -> Dict[str, Any]:
        if isinstance(oid, (ObjectId, int)):
            oid = str(oid)
        if oid.isdigit():
            route = NotificationGroup.get_by_id(int(oid))
        elif oid.startswith("ng:"):
            route = NotificationGroup.get_by_id(int(oid[3:]))
        else:
            route = MessageRoute.get_by_id(oid)
        if not route or not route.is_active:
            raise KeyError()
        return route.get_route_config()
