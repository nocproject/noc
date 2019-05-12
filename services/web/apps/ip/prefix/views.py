# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.prefix application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from operator import attrgetter
# Third-party modules
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import ModelParameter, PrefixParameter
from noc.core.ip import IP
from noc.lib.app.decorators.state import state_handler


@state_handler
class PrefixApplication(ExtModelApplication):
    """
    Prefix application
    """
    title = _("Prefix")
    model = Prefix

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def can_create(self, user, obj):
        # return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)
        return Prefix.has_access(user, obj.vrf, obj.afi, obj.prefix, "can_create")

    def can_update(self, user, obj):
        return Prefix.has_access(user, obj.vrf, obj.afi, obj.prefix, "can_change")

    def can_delete(self, user, obj):
        return Prefix.has_access(user, obj.vrf, obj.afi, obj.prefix, "can_delete")

    def queryset(self, request, query=None):
        qs = super(PrefixApplication, self).queryset(request, query=query)
        return qs.filter(Prefix.read_Q(request.user))

    def clean(self, data):
        if data.get("direct_permissions"):
            data["direct_permissions"] = [[x["user"], x["group"], x["permission"]] for x in data["direct_permissions"]]
        return super(PrefixApplication, self).clean(data)

    def instance_to_dict(self, o, fields=None):
        r = super(PrefixApplication, self).instance_to_dict(o, fields=fields)
        r["direct_permissions"] = []
        if o.direct_permissions:
            for user, group, perm in o.direct_permissions:
                user = User.objects.filter(id=user)
                group = Group.objects.filter(id=group)
                r["direct_permissions"] += [{
                    "user": user[0].id if user else None,
                    "user__label": user[0].username if user else "",
                    "group": group[0].id if group else None,
                    "group__label": group[0].name if group else "",
                    "permission": perm
                }]
        return r

    @view(
        url=r"^(?P<prefix_id>\d+)/rebase/$",
        method=["POST"], access="rebase", api=True,
        validate={
            "to_vrf": ModelParameter(VRF),
            "to_prefix": PrefixParameter()
        }
    )
    def api_rebase(self, request, prefix_id, to_vrf, to_prefix):
        prefix = self.get_object_or_404(Prefix, id=int(prefix_id))
        try:
            new_prefix = prefix.rebase(to_vrf, to_prefix)
            return self.instance_to_dict(new_prefix)
        except ValueError as e:
            return self.response_bad_request(str(e))

    @view(
        url=r"^(?P<prefix_id>\d+)/suggest_free/$",
        method=["GET"], access="read", api=True
    )
    def api_suggest_free(self, request, prefix_id):
        """
        Suggest free blocks of different sizes
        :param request:
        :param prefix_id:
        :return:
        """
        prefix = self.get_object_or_404(Prefix, id=int(prefix_id))
        suggestions = []
        p_mask = int(prefix.prefix.split("/")[1])
        free = sorted(
            IP.prefix(prefix.prefix).iter_free([
                pp.prefix for pp in prefix.children_set.all()
            ]),
            key=attrgetter("mask"),
            reverse=True
        )
        # Find smallest free block possible
        for mask in range(30 if prefix.is_ipv4 else 64,
                          max(p_mask + 1, free[-1].mask) - 1, -1):
            # Find smallest free block possible
            for p in free:
                if p.mask <= mask:
                    suggestions += [{
                        "prefix": "%s/%d" % (p.address, mask),
                        "size": 2 ** (32 - mask) if prefix.is_ipv4 else None
                    }]
                    break
        return suggestions

    @view(method=["DELETE"], url=r"^(?P<id>\d+)/recursive/$", access="delete", api=True)
    def api_delete_recursive(self, request, id):
        try:
            o = self.queryset(request).get(**{self.pk: int(id)})
        except self.model.DoesNotExist:
            return self.render_json({
                "status": False,
                "message": "Not found"
            }, status=self.NOT_FOUND)
        # Check permissions
        if not self.can_delete(request.user, o):
            return self.render_json({
                "status": False,
                "message": "Permission denied"
            }, status=self.FORBIDDEN)
        try:
            o.delete_recursive()
        except ValueError as e:
            return self.render_json(
                {
                    "success": False,
                    "message": "ERROR: %s" % e
                }, status=self.CONFLICT)
        return HttpResponse(status=self.DELETED)

    @view(r"^(?P<id>\d+)/get_path/$", access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(Prefix, id=int(id))
        try:
            path = [Prefix.objects.get(id=ns) for ns in o.get_path()]
            return {"data": [{"id": str(p.id), "name": unicode(p.name), "afi": p.afi} for p in path]}
        except ValueError as e:
            return self.response_bad_request(str(e))
