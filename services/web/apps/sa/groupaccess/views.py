# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.groupaccess application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models.groupaccess import GroupAccess


class GroupAccessApplication(ExtModelApplication):
    """
    GroupAccess application
    """
    title = "Group Access"
    menu = "Setup | Group Access"
    model = GroupAccess
