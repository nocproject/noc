# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.vendor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.vendor import Vendor
from noc.main.models.collectioncache import CollectionCache


class VendorApplication(ExtDocApplication):
    """
    Vendor application
    """
    title = "Vendor"
    menu = "Setup | Vendors"
    model = Vendor
    query_fields = [
        "name__icontains", "code__icontains", "site__icontains"
    ]

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        vendor = self.get_object_or_404(Vendor, id=id)
        return vendor.to_json()
