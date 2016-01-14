# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## crm.supplier application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.crm.models.supplier import Supplier


class SupplierApplication(ExtDocApplication):
    """
    Supplier application
    """
    title = "Supplier"
    menu = "Setup | Supplier"
    model = Supplier
    query_fields = ["name__icontains"]

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile.style else ""
