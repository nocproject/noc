# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vctype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.vc.models import VCType


class VCTypeApplication(ExtModelApplication):
    """
    VCType application
    """
    title = "VCType"
    menu = "Setup | VC Types"
    model = VCType
    query_fields = ["name"]
    query_condition = "icontains"
