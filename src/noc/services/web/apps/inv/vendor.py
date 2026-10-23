# ---------------------------------------------------------------------
# inv.vendor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.inv.models.vendor import Vendor
from noc.core.translation import ugettext as _


class VendorApplication(ExtDocApplication):
    """
    Vendor application
    """

    title = _("Vendor")
    menu = [_("Setup"), _("Vendors")]
    model = Vendor
    query_fields = ["name__icontains", "code__icontains", "site__icontains"]
    default_ordering = ["name"]

    @api.get("^(?P<id>[0-9a-f]{24})/json/$", access="read")
    def api_json(self, request: HttpRequest, id):
        vendor = self.get_object_or_404(Vendor, id=id)
        return vendor.to_json()
