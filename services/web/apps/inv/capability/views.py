# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.capability application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.capability import Capability
from noc.main.models.doccategory import DocCategory


class CapabilityApplication(ExtDocApplication):
    """
    Capability application
    """
    title = "Capability"
    menu = "Setup | Capabilities"
    model = Capability
    query_fields = ["name", "description"]
    parent_model = DocCategory
    parent_field = "parent"
