# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.prefixaccess application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.ip.models import PrefixAccess


class PrefixAccessApplication(ExtModelApplication):
    """
    PrefixAccess application
    """
    title = "Prefix Access"
    menu = "Setup | Prefix Access"
    model = PrefixAccess
    query_fields = ["user__username", "prefix"]
    query_condition = "icontains"
