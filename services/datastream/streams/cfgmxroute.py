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
        r = {
            "id": str(route.id),
            "name": route.name,
            "type": route.type,
            "order": route.order,
            "action": route.action,
            "match": [],
        }
        if route.stream:
            r["stream"] = route.stream
        if route.headers:
            r["headers"] = [{"header": m.header, "value": m.value} for m in route.headers]
        if route.notification_group:
            r["notification_group"] = str(route.notification_group.id)
        if route.transmute_template:
            r["transmute_template"] = str(route.transmute_template.id)
        if route.transmute_handler:
            r["transmute_handler"] = str(route.transmute_handler.id)
        for match in route.match:
            r["match"] += [
                {
                    "labels": match.labels,
                    "exclude_labels": match.exclude_labels,
                    "administrative_domain": str(match.administrative_domain.id)
                    if match.administrative_domain
                    else None,
                    "headers": [
                        {"header": m.header, "op": m.op, "value": m.value}
                        for m in match.headers_match
                    ],
                }
            ]
        return r
