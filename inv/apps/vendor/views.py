# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.vendor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011
## The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import TreeApplication
from noc.inv.models import Vendor


class VendorApplication(TreeApplication):
    title = "Vendors"
    verbose_name = "Vendor"
    verbose_name_plural = "Vendors"
    menu = "Setup | Vendors"
    model = Vendor
