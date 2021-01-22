# ---------------------------------------------------------------------
# maintenance.maintenance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import orjson
import bson

# Third-party modules
from django.http import HttpResponse
from mongoengine.errors import ValidationError
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintenance.models.maintenance import Maintenance, MaintenanceObject, MaintenanceSegment
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
                return qs.filter(affected_objects__object__in=mos)
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
                if mai in o.affected_objects:
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

    @view(
        method=["GET"],
        url=r"^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
        access="read",
        api=True,
    )
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        o = self.queryset(request).filter(**{self.pk: id}).first()
        return self.response(
            self.instance_to_dict(o, exclude_fields=["affected_objects"]), status=self.OK
        )

    @view(
        method=["PUT"],
        url=r"^(?P<id>[0-9a-f]{24}|\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?$",
        access="update",
        api=True,
    )
    def api_update(self, request, id):
        try:
            attrs = self.clean(self.deserialize(request.body))
        except ValueError as e:
            self.logger.info("Bad request: %r (%s)", request.body, e)
            return self.response(str(e), status=self.BAD_REQUEST)
        try:
            o = self.queryset(request).filter(**{self.pk: id}).first()
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        for k in attrs:
            if not self.has_field_editable(k):
                continue
            if k != self.pk and "__" not in k:
                setattr(o, k, attrs[k])
        try:
            o.save()
        except ValidationError as e:
            return self.response({"message": str(e)}, status=self.BAD_REQUEST)
        # Reread result
        o = self.model.objects.filter(**{self.pk: id}).first()
        if request.is_extjs:
            r = {
                "success": True,
                "data": self.instance_to_dict(o, exclude_fields=["affected_objects"]),
            }
        else:
            r = self.instance_to_dict(o, exclude_fields=["affected_objects"])
        return self.response(r, status=self.OK)

    @view(method=["GET"], url="^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, self.instance_to_dict_list)

    def instance_to_dict_list(self, o, fields=None):
        return super().instance_to_dict(
            o, exclude_fields=["direct_objects", "direct_segments", "affected_objects"]
        )

    @view(url="(?P<id>[0-9a-f]{24})/objects/", method=["GET"], access="read", api=True)
    def api_test(self, request, id):
        r = []
        data = [
            d
            for d in Maintenance._get_collection().aggregate(
                [
                    {"$match": {"_id": bson.ObjectId(id)}},
                    {
                        "$project": {"objects": "$affected_objects.object"},
                    },
                ]
            )
        ]
        for mo in (
            ManagedObject.objects.filter(is_managed=True, id__in=data[0].get("objects"))
            .values("id", "name", "is_managed", "profile", "address", "description", "tags")
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
                    "tags": mo["tags"],
                }
            ]
        out = {"total": len(r), "success": True, "data": r}
        return self.response(out, status=self.OK)
