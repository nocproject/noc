# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.interfaceprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.interfaceprofile import InterfaceProfile


class InterfaceProfileApplication(ExtDocApplication):
    """
    InterfaceProfile application
    """
    title = "Interface Profile"
    menu = "Setup | Interface Profiles"
    model = InterfaceProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
