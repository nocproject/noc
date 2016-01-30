# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.outage
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import cachetools
import bson
## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.activealarm import ActiveAlarm
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.interface import Interface
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment


class OutageApplication(ExtApplication):
    title = "Outages"
    menu = "Outages"
    glyph = "bolt"

    OUTAGE_CLASSES = [
        "NOC | Managed Object | Ping Failed"
    ]

    @view("^$", access="read", api=True)
    def api_outage(self, request):
        # Get alarm classes of interest
        acs = list(set(
            ac.id for ac in
            AlarmClass.objects.filter(name__in=self.OUTAGE_CLASSES)
        ))
        # Get affected managed objects
        mos = list(set(
            d["managed_object"]
            for d in ActiveAlarm._get_collection().find({
                    "alarm_class": {"$in": acs}
                }, {
                    "_id": 0,
                    "managed_object": 1
                }
            )
        ))
        # Get customer ports
        if not mos:
            return {
                "root": {
                    "children": []
                }
            }
        # Get customer interface profiles
        ips = list(set(
            d["_id"]
            for d in InterfaceProfile._get_collection().find({
                "is_customer": True
            }, {
                "_id": 1
            })
        ))
        # Calculate affected customers
        affected = {}  # mo_id -> customers
        rs = Interface._get_collection().aggregate([
            # Filter customer ports
            {
                "$match": {
                    "managed_object": {
                        "$in": mos
                    },
                    "profile": {
                        "$in": ips
                    }
                }
            },
            # Aggregate
            {
                "$group": {
                    "_id": "$managed_object",
                    "customers": {
                        "$sum": 1
                    }
                }
            }
        ])
        for d in rs["result"]:
            affected[d["_id"]] = d["customers"]
        # Build result
        r = {
            "root": {
                "text": "Root",
                "expanded": True,
                "children": []
            }
        }
        #
        self.seg_cache = cachetools.LRUCache(
            10000,
            missing=self.get_segment
        )
        for mo_id, name, address, segment in ManagedObject.objects.filter(
            id__in=mos
        ).values_list("id", "name", "address", "segment"):
            # Search and populate segments tree
            p = r["root"]
            for seg in self.get_segment_path(segment):
                found = False
                for c in p["children"]:
                    if c["text"] == seg:
                        p = c
                        found = True
                        break
                if not found:
                    cc = {
                        "text": seg,
                        "expanded": True,
                        "children": []
                    }
                    p["children"] += [cc]
                    p = cc
            # Add faulty management object
            p["children"] += [{
                "text": name,
                "leaf": True,
                "address": address,
                "n_objects": 1,
                "affected_clients": affected.get(mo_id, 0)
            }]
            p["expanded"] = False
        for p in r["root"]["children"]:
            n_objects, n_affected = self.get_power(p)
            p["n_objects"] = n_objects
            p["affected_clients"] = n_affected
        return r

    def get_segment_path(self, segment_id):
        path = []
        while segment_id:
            d = self.seg_cache[segment_id]
            path = [d["name"]] + path
            segment_id = d.get("parent")
        return path

    @staticmethod
    def get_segment(seg_id):
        return NetworkSegment._get_collection().find({
            "_id": bson.ObjectId(seg_id)
        }, {
            "_id": 1,
            "name": 1,
            "parent": 1
        })[0]

    def get_power(self, node):
        """
        Calculate node's alarm power
        """
        n_mo = node.get("n_objects", 0)
        n_affected = node.get("affected_clients", 0)
        for c in node.get("children", []):
            x, y = self.get_power(c)
            c["n_objects"] = x
            c["affected_clients"] = y
            n_mo += x
            n_affected += y
        return n_mo, n_affected
