# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.systemtemplate application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import SystemTemplate


class SystemTemplateApplication(ExtModelApplication):
    """
    SystemTemplate application
    """
    title = "System Templates"
    menu = "Setup | System Templates"
    model = SystemTemplate
    query_fields = ["name__icontains"]

