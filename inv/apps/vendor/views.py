# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.vendor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models import Vendor


class VendorApplication(ExtDocApplication):
    """
    Vendor application
    """
    title = "Vendor"
    menu = "Setup | Vendors"
    model = Vendor
    query_fields = ["name__icontains", "site__icontains"]
