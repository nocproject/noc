# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.vendor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.vendor import Vendor
from noc.core.translation import ugettext as _


class VendorApplication(ExtDocApplication):
    """
    Vendor application
    """
    title = _("Vendor")
    menu = [_("Setup"), _("Vendors")]
    model = Vendor
    query_fields = [
        "name__icontains", "code__icontains", "site__icontains"
    ]
    default_ordering = ["name"]

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        vendor = self.get_object_or_404(Vendor, id=id)
        return vendor.to_json()
