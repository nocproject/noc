# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## crm.supplierprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.crm.models.supplierprofile import SupplierProfile


class SupplierProfileApplication(ExtDocApplication):
    """
    SupplierProfile application
    """
    title = "Supplier Profile"
    menu = "Setup | Supplier Profiles"
    model = SupplierProfile
    query_fields = ["name__icontains", "description__icontains"]

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
