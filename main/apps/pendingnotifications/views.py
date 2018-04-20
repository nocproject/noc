# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pendingnotifications application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import Notification


class NotificationApplication(ExtModelApplication):
    """
    Notification application
    """
    title = "Pending Notifications"
    menu = "Pending Notifications"
    model = Notification
