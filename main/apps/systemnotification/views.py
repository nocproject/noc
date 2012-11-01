# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.systemnotification application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import SystemNotification

class SystemNotificationApplication(ExtModelApplication):
    """
    SystemNotification application
    """
    title = "System Notifications"
    menu = "Setup | System Notifications"
    model = SystemNotification
    query_fields = ["name__icontains"]

