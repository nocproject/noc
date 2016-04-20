# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Maintainance card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
import jinja2
## NOC modules
from base import BaseCard
from noc.maintainance.models.maintainance import Maintainance
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import ServiceSummary


class MaintainanceCard(BaseCard):
    default_template_name = "maintainance"
    model = Maintainance
    default_title_template = "Maintainance: {{ object.subject }}"

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
        summary = {
            "service": {},
            "subscriber": {}
        }
        for ao in self.object.affected_objects:
            mo = ao.object
            ss = ServiceSummary.get_object_summary(mo)
            affected += [{
                "id": mo.id,
                "object": mo,
                "name": mo.name,
                "address": mo.address,
                "platform": mo.platform,
                "summary": ss
            }]
            update_dict(summary["service"], ss.get("service", {}))
            update_dict(summary["subscriber"], ss.get("subscriber", {}))
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
            "summary": summary
        }
