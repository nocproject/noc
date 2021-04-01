# ---------------------------------------------------------------------
# Maintenance card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import jinja2

# NOC modules
from .base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.platform import Platform
from noc.maintenance.models.maintenance import Maintenance, AffectedObjects
from noc.sa.models.servicesummary import ServiceSummary


class MaintenanceCard(BaseCard):
    name = "maintenance"
    default_template_name = "maintenance"
    model = Maintenance
    default_title_template = "Maintenance: {{ object.subject }}"

    def get_data(self):
        def update_dict(s, d):
            for k in d:
                if k in s:
                    s[k] += d[k]
                else:
                    s[k] = d[k]

        stpl = self.object.type.card_template or self.default_title_template
        now = datetime.datetime.now()
        if self.object.start > now:
            status = "before"
        elif self.object.is_completed:
            status = "complete"
        else:
            status = "progress"
        # Calculate affected objects
        affected = []
        summary = {"service": {}, "subscriber": {}}
        # Maintenance
        data = [
            d
            for d in AffectedObjects._get_collection().aggregate(
                [
                    {"$match": {"maintenance": self.object.id}},
                    {
                        "$project": {"objects": "$affected_objects.object"},
                    },
                ]
            )
        ]
        hide = False
        if data:
            if len(data[0].get("objects")) > 100:
                hide = True
            for mo in (
                ManagedObject.objects.filter(is_managed=True, id__in=data[0].get("objects"))
                .values("id", "name", "platform", "address", "container")
                .distinct()
            ):
                ss, object = {}, None
                if not hide:
                    ss = ServiceSummary.get_object_summary(mo["id"])
                    object = ManagedObject.get_by_id(mo["id"])
                    update_dict(summary["service"], ss.get("service", {}))
                    update_dict(summary["subscriber"], ss.get("subscriber", {}))
                ao = {
                    "id": mo["id"],
                    "name": mo["name"],
                    "address": mo["address"],
                    "platform": Platform.get_by_id(mo["platform"]).name if mo["platform"] else "",
                    "summary": ss,
                }
                if object:
                    ao["object"] = object
                affected += [ao]
        #
        return {
            "title": jinja2.Template(stpl).render({"object": self.object}),
            "object": self.object,
            "subject": self.object.subject,
            "contacts": self.object.contacts,
            "start": self.object.start,
            "stop": self.object.stop,
            "description": self.object.description,
            "status": status,
            "affected": affected,
            "summary": summary,
        }
