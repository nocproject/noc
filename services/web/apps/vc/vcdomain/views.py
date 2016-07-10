# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vcdomain application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.vc.models import VCDomain


class VCDomainApplication(ExtModelApplication):
    """
    VCDomain application
    """
    title = "VCDomain"
    menu = "Setup | VC Domains"
    model = VCDomain
    icon = "icon_world_link"
    query_fields = ["name", "description"]
    query_condition = "icontains"

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""

    def field_object_count(self, o):
        return o.managedobject_set.count()
