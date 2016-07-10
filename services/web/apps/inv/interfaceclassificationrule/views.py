# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.interfaceclassificationrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.interfaceclassificationrule import InterfaceClassificationRule


class InterfaceClassificationRuleApplication(ExtDocApplication):
    """
    InterfaceClassificationRule application
    """
    title = "Interface Classification Rule"
    menu = "Setup | Interface Classification Rules"
    model = InterfaceClassificationRule

    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["order"]

    def field_row_class(self, o):
        if o.profile and o.profile.style:
            return o.profile.style.css_class_name
        else:
            return ""

    def field_match_expr(self, o):
        return o.match_expr