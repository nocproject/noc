# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Segment card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## NOC modules
from base import BaseCard
from noc.sa.models.servicesummary import ServiceSummary
from noc.inv.models.networksegment import NetworkSegment
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.objectstatus import ObjectStatus


class SegmentCard(BaseCard):
    name = "segment"
    default_template_name = "segment"
    model = NetworkSegment

    def get_data(self):
        # Calculate contained objects
        summary = {
            "service": {},
            "subscriber": {}
        }
        objects = []
        for mo in self.object.managed_objects.filter(is_managed=True):
            ss = ServiceSummary.get_object_summary(mo)
            objects += [{
                "id": mo.id,
                "name": mo.name,
                "object": mo,
                "summary": ss
            }]
            self.update_dict(summary["service"], ss.get("service", {}))
            self.update_dict(summary["subscriber"], ss.get("subscriber", {}))
        # Update object statuses
        mos = [o["id"] for o in objects]
        alarms = set(d["managed_object"] for d in ActiveAlarm._get_collection().find({
            "managed_object": {
                "$in": mos
            }
        }, {"_id": 0, "managed_object": 1}))
        o_status = ObjectStatus.get_statuses(mos)
        for o in objects:
            if o["id"] in o_status:
                if o["id"] in alarms:
                    o["status"] = "alarm"
                else:
                    o["status"] = "up"
            else:
                o["status"] = "down"
        # Calculate children
        children = []
        for ns in NetworkSegment.objects.filter(parent=self.object.id):
            children += [{
                "id": ns.id,
                "name": ns.name,
                "object": ns
            }]
        return {
            "object": self.object,
            "managed_objects": sorted(objects, key=operator.itemgetter("name")),
            "children": sorted(children, key=operator.itemgetter("name")),
            "parent": self.object.parent,
            "summary": summary
        }
