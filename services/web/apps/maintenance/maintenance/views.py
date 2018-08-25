# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# maintenance.maintenance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintenance.models.maintenance import Maintenance
from noc.core.translation import ugettext as _


class MaintenanceApplication(ExtDocApplication):
    """
    Maintenance application
    """
    title = _("Maintenance")
    menu = _("Maintenance")
    model = Maintenance
    query_condition = "icontains"
    query_fields = ["subject"]

    @view(method=["GET"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict_list)

    def instance_to_dict_list(self, o, fields=None):
        return {
            "id": str(o.id),
            "description": o.description,
            "contacts": o.contacts,
            "type": str(o.type.id),
            "type__label": o.type.name,
            "stop": o.stop.strftime("%Y-%m-%d %H:%M:%S") if o.stop else "",
            "start": o.start.strftime("%Y-%m-%d %H:%M:%S") if o.start else "",
            "suppress_alarms": o.suppress_alarms,
            "escalate_managed_object": o.escalate_managed_object.id if o.escalate_managed_object else None,
            "escalate_managed_object__label": o.escalate_managed_object.name if o.escalate_managed_object else "",
            "escalation_tt": None,
            "is_completed": o.is_completed,
            "direct_objects": [],
            "direct_segments": [],
            "subject": o.subject,
            "time_pattern": o.time_pattern.id if o.time_pattern else None,
            "time_pattern__label": o.time_pattern.name if o.time_pattern else "",
            # "row_class": ""
        }

    @view(url="(?P<id>[0-9a-f]{24})/objects/", method=["GET"],
          access="read", api=True)
    def api_test(self, request, id):
        o = self.get_object_or_404(Maintenance, id=id)
        r = []
        for mao in o.affected_objects:
            mo = mao.object
            r += [
                {
                    "id": mo.id,
                    "name": mo.name,
                    "is_managed": mo.is_managed,
                    "profile": mo.profile.name,
                    # "platform": mo.platform,
                    # "administrative_domain": unicode(mo.administrative_domain),
                    "address": mo.address,
                    "description": mo.description,
                    "tags": mo.tags
                }
            ]
        return r
