# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.useraccess application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models.useraccess import UserAccess


class UserAccessApplication(ExtModelApplication):
    """
    UserAccess application
    """
    title = "User Access"
    menu = "Setup | User Access"
    model = UserAccess
