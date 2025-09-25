# ---------------------------------------------------------------------
# Maintenance card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import jinja2

# NOC modules
from .base import BaseCard
from noc.sa.models.managedobject import ManagedObject
from noc.maintenance.models.maintenance import Maintenance
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
        SQL = """SELECT id, name, platform, address
            FROM sa_managedobject
            WHERE affected_maintenances @> '{"%s": {}}' ORDER BY address;""" % str(self.object.id)
        for mo in ManagedObject.objects.raw(SQL):
            ss = ServiceSummary.get_object_summary(mo.id)
            update_dict(summary["service"], ss.get("service", {}))
            update_dict(summary["subscriber"], ss.get("subscriber", {}))
            ao = {
                "id": mo.id,
                "object": mo,
                "name": mo.name,
                "address": mo.address,
                "platform": mo.platform.name if mo.platform else "",
                "summary": ss,
            }
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
