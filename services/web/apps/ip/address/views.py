# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.address application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.ip.models.address import Address
from noc.ip.models.prefixaccess import PrefixAccess
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
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def can_update(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def can_delete(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def queryset(self, request, query=None):
        qs = super(AddressApplication, self).queryset(request, query=query)
        return qs.filter(PrefixAccess.read_Q(request.user, field="address"))
