# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.address application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.contrib.auth.models import User, Group
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models.address import Address
from noc.ip.models.prefix import Prefix
from noc.lib.app.decorators.state import state_handler


@state_handler
class AddressApplication(ExtModelApplication):
    """
    Address application
    """
    title = "Address"
    model = Address
    ignored_fields = ExtModelApplication.ignored_fields | {"prefix"}

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""

    def can_create(self, user, obj):
        return Address.has_access(user, obj.vrf, obj.afi, obj.prefix, "can_create")

    def can_update(self, user, obj):
        return Address.has_access(user, obj.vrf, obj.afi, obj.prefix, "can_change")

    def can_delete(self, user, obj):
        return Address.has_access(user, obj.vrf, obj.afi, obj.prefix, "can_delete")

    def queryset(self, request, query=None):
        qs = super(AddressApplication, self).queryset(request, query=query)
        return qs.filter(Prefix.read_Q(request.user))

    def clean(self, data):
        if data.get("direct_permissions"):
            data["direct_permissions"] = [[x["user"], x["group"], x["permission"]] for x in data["direct_permissions"]]
        return super(AddressApplication, self).clean(data)

    def instance_to_dict(self, o, fields=None):
        r = super(AddressApplication, self).instance_to_dict(o, fields=fields)
        r["direct_permissions"] = []
        if o.direct_permissions:
            for user, group, perm in o.direct_permissions:
                user = User.objects.get(id=user)
                group = Group.objects.get(id=group)
                r["direct_permissions"] += [{
                    "user": user.id,
                    "user__label": user.username,
                    "group": group.id,
                    "group__label": group.name,
                    "permission": perm
                }]
        return r
