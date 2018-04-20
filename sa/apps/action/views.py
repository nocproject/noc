# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.action application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models.action import Action


class ActionApplication(ExtDocApplication):
    """
    Action application
    """
    title = "Action"
    menu = "Setup | Actions"
    model = Action
