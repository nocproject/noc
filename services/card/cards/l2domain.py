# ---------------------------------------------------------------------
# L2Domain card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator

# NOC modules
from .base import BaseCard
from noc.sa.models.servicesummary import ServiceSummary
from noc.sa.models.managedobject import ManagedObject
from noc.vc.models.l2domain import L2Domain
from noc.fm.models.activealarm import ActiveAlarm


class L2DomainCard(BaseCard):
    name = "l2domain"
    default_template_name = "l2domain"
    model = L2Domain

    def get_object(self, id):
        return L2Domain.objects.get(id=id)

    def get_data(self):
        # Calculate contained objects
        objects = []
        for mo in self.object.managed_objects.filter(is_managed=True):
            ss = ServiceSummary.get_object_summary(mo)
            objects += [{"id": mo.id, "name": mo.name, "object": mo, "summary": ss}]
        # Update object statuses
        mos = [o["id"] for o in objects]
        alarms = {
            d["managed_object"]
            for d in ActiveAlarm._get_collection().find(
                {"managed_object": {"$in": mos}}, {"_id": 0, "managed_object": 1}
            )
        }
        o_status = ManagedObject.get_statuses(mos)
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
        # Calculate VLANs
        vlans = []
        return {
            "object": self.object,
            "managed_objects": sorted(objects, key=operator.itemgetter("name")),
            "children": sorted(children, key=operator.itemgetter("name")),
            "parent": None,
            "summary": {},
            "vlans": vlans,
        }
