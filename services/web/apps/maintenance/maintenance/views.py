# ---------------------------------------------------------------------
# maintenance.maintenance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import orjson

# Third-party modules
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.maintenance.models.maintenance import (
    Maintenance,
    MaintenanceObject,
    MaintenanceSegment,
)
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
from noc.main.models.label import Label
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

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        qs = super().queryset(request)
        if not request.user.is_superuser:
            user_ads = UserAccess.get_domains(request.user)
            qs = qs.filter(Q(administrative_domain=[]) | Q(administrative_domain__in=user_ads))
        if query and self.query_fields:
            q = qs.filter(self.get_Q(request, query))
            if q:
                return q
            sq = ManagedObject.get_search_Q(query)
            if sq:
                obj = ManagedObject.objects.filter(sq)
            else:

                obj = ManagedObject.objects.filter(
                    name__contains=query, affected_maintenances__isnull=False
                )
            if obj:
                for o in obj:
                    data = (am for am in o.affected_maintenances)
                return Maintenance.objects.filter(id__in=list(data))
            return qs.filter(type=None)
        else:
            return qs

    @view(url=r"^(?P<id>[a-z0-9]{24})/add/", method=["POST"], api=True, access="update")
    def api_add(self, request, id):
        body = orjson.loads(request.body)
        o = self.model.objects.filter(**{self.pk: id}).first()
        if body["mode"] == "Object":
            for mo in body["elements"]:
                mai = MaintenanceObject(object=mo.get("object"))
                if ManagedObject.objects.filter(
                    id=mo.get("object"), affected_maintenances__has_key=id
                ).first():
                    continue
                if mai not in o.direct_objects:
                    o.direct_objects += [mai]
            o.save()
        if body["mode"] == "Segment":
            for seg in body["elements"]:
                mas = MaintenanceSegment(object=seg.get("segment"))
                if mas not in o.direct_segments:
                    o.direct_segments += [mas]
            o.save()
        return self.response({"result": "Add object"}, status=self.OK)

    @view(url="(?P<id>[0-9a-f]{24})/objects/", method=["GET"], access="read", api=True)
    def api_test(self, request, id):
        r = []
        for mo in (
            ManagedObject.objects.filter(is_managed=True, affected_maintenances__has_key=id)
            .values("id", "name", "is_managed", "profile", "address", "description", "labels")
            .distinct()
        ):
            r += [
                {
                    "id": mo["id"],
                    "name": mo["name"],
                    "is_managed": mo["is_managed"],
                    "profile": Profile.get_by_id(mo["profile"]).name,
                    "address": mo["address"],
                    "description": mo["description"],
                    "labels": [
                        {
                            "id": ll.name,
                            "is_protected": ll.is_protected,
                            "scope": ll.scope,
                            "name": ll.name,
                            "value": ll.value,
                            "badges": ll.badges,
                            "bg_color1": f"#{ll.bg_color1:06x}",
                            "fg_color1": f"#{ll.fg_color1:06x}",
                            "bg_color2": f"#{ll.bg_color2:06x}",
                            "fg_color2": f"#{ll.fg_color2:06x}",
                        }
                        for ll in Label.objects.filter(name__in=mo["labels"])
                    ],
                }
            ]

        out = {"total": len(r), "success": True, "data": r}
        return self.response(out, status=self.OK)

    def instance_to_dict_list(self, o, fields=None, nocustom=False):
        return {
            "id": str(o.id),
            "description": o.description,
            "contacts": o.contacts,
            "type": str(o.type.id),
            "type__label": o.type.name,
            "stop": o.stop.strftime("%Y-%m-%d %H:%M:%S") if o.stop else "",
            "start": o.start.strftime("%Y-%m-%d %H:%M:%S") if o.start else "",
            "suppress_alarms": o.suppress_alarms,
            "escalate_managed_object": (
                o.escalate_managed_object.id if o.escalate_managed_object else None
            ),
            "escalate_managed_object__label": (
                o.escalate_managed_object.name if o.escalate_managed_object else ""
            ),
            "escalation_policy": o.escalation_policy,
            "escalation_tt": o.escalation_tt if o.escalation_tt else None,
            "is_completed": o.is_completed,
            "direct_objects": [],
            "direct_segments": [],
            "subject": o.subject,
            "time_pattern": o.time_pattern.id if o.time_pattern else None,
            "time_pattern__label": o.time_pattern.name if o.time_pattern else "",
        }
