# ---------------------------------------------------------------------
# maintenance.maintenance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import orjson
import bson

# Third-party modules
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintenance.models.maintenance import (
    Maintenance,
    MaintenanceObject,
    MaintenanceSegment,
    AffectedObjects,
)
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.useraccess import UserAccess
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

                obj = ManagedObject.objects.filter(name__contains=query)
            if obj:
                mos = obj.values_list("id", flat=True)
                ao = AffectedObjects.objects.filter(affected_objects__object__in=mos).values_list(
                    "maintenance"
                )
                return ao
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
                if AffectedObjects.objects.filter(maintenance=o, affected_objects=mai):
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
        out = {"total": 0, "success": True, "data": None}
        data = [
            d
            for d in AffectedObjects._get_collection().aggregate(
                [
                    {"$match": {"maintenance": bson.ObjectId(id)}},
                    {
                        "$project": {"objects": "$affected_objects.object"},
                    },
                ]
            )
        ]
        if data:
            for mo in (
                ManagedObject.objects.filter(is_managed=True, id__in=data[0].get("objects"))
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
                        "labels": mo["labels"],
                    }
                ]
                out = {"total": len(r), "success": True, "data": r}
        return self.response(out, status=self.OK)
