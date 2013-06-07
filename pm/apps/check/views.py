# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.check application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.check import PMCheck


class PMCheckApplication(ExtDocApplication):
    """
    PMCheck application
    """
    title = "Checks"
    menu = "Checks"
    model = PMCheck
    query_fields = ["name"]