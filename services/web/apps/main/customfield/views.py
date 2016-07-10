# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.customfield application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import CustomField


class CustomFieldApplication(ExtModelApplication):
    """
    CustomField application
    """
    title = "Custom Fields"
    menu = "Setup | Custom Fields"
    model = CustomField
    icon = "icon_cog_add"
    query_fields = ["name", "description", "table"]
