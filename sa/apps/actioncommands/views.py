# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.actioncommands application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models.actioncommands import ActionCommands


class ActionCommandsApplication(ExtDocApplication):
    """
    ActionCommands application
    """
    title = "Action Command"
    menu = "Setup | Action Commands"
    model = ActionCommands
