# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Segment card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
# NOC modules
from .base import BaseCard
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem
from noc.inv.models.networksegment import NetworkSegment
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.objectstatus import ObjectStatus
from noc.vc.models.vlan import VLAN


class SegmentCard(BaseCard):
    name = "segment"
    default_template_name = "segment"
    model = NetworkSegment

    def get_object(self, id):
        if self.current_user.is_superuser:
            return NetworkSegment.objects.get(id=id)
        else:
            return NetworkSegment.objects.get(
                id=id,
                adm_domains__in=self.get_user_domains()
            )

    def get_data(self):
        # Calculate contained objects
        summary = {
            "service": SummaryItem.items_to_dict(self.object.total_services),
            "subscriber": SummaryItem.items_to_dict(self.object.total_subscribers)
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
                "object": ns,
                "summary": {
                    "service": SummaryItem.items_to_dict(ns.total_services),
                    "subscriber": SummaryItem.items_to_dict(ns.total_subscribers),
                }
            }]
        # Calculate VLANs
        vlans = []
        if self.object.vlan_border:
            vlans = list(VLAN.objects.filter(segment=self.object.id).order_by("vlan"))
        #
        return {
            "object": self.object,
            "managed_objects": sorted(objects, key=operator.itemgetter("name")),
            "children": sorted(children, key=operator.itemgetter("name")),
            "parent": self.object.parent,
            "summary": summary,
            "vlans": vlans
        }
