# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.objectnotification application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import ObjectNotification


class ObjectNotificationApplication(ExtModelApplication):
    """
    ObjectNotification application
    """
    title = "Object Notification"
    menu = "Setup | Object Notification"
    model = ObjectNotification
