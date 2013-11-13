# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.unknownmodel application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models import UnknownModel


class UnknownModelApplication(ExtDocApplication):
    """
    UnknownModel application
    """
    title = "Unknown Models"
    menu = "Unknown Models"
    model = UnknownModel

    query_condition = "icontains"
    query_fields = ["vendor", "managed_object", "part_no", "description"]