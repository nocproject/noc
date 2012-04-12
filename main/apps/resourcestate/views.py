# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.resourcestate application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import ResourceState


class ResourceStateApplication(ExtModelApplication):
    """
    ResourceState application
    """
    title = "Resource States"
    menu = "Setup | Resource States"
    model = ResourceState
    query_fields = ["name", "description"]
    query_condition = "icontains"
