# ---------------------------------------------------------------------
# ip.address application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.ip.models.address import Address
from noc.ip.models.prefixaccess import PrefixAccess
from noc.services.web.base.decorators.state import state_handler


@state_handler
class AddressApplication(ExtModelApplication):
    """
    Address application
    """

    title = "Address"
    model = Address
    ignored_fields = ExtModelApplication.ignored_fields | {"prefix"}

    def can_create(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def can_update(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def can_delete(self, user, obj):
        return PrefixAccess.user_can_change(user, obj.vrf, obj.afi, obj.prefix)

    def queryset(self, request, query=None):
        qs = super().queryset(request, query=query)
        return qs.filter(PrefixAccess.read_Q(request.user, field="address", table="ip_address"))
