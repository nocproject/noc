# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.notificationgroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import (NotificationGroup, NotificationGroupUser,
                             NotificationGroupOther)
from noc.lib.app.modelinline import ModelInline
from noc.sa.interfaces.base import (ListOfParameter, ModelParameter,
                                    UnicodeParameter)


class NotificationGroupApplication(ExtModelApplication):
    """
    NotificationGroup application
    """
    title = "Notification Group"
    menu = "Setup | Notification Groups"
    model = NotificationGroup

    users = ModelInline(NotificationGroupUser)
    other = ModelInline(NotificationGroupOther)

    @view(url="^actions/test/$", method=["POST"],
        access="update", api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(NotificationGroup)),
            "subject": UnicodeParameter(),
            "body": UnicodeParameter()
        })
    def api_action_test(self, request, ids, subject, body):
        for g in ids:
            g.notify(subject=subject, body=body)
        return "Notification message has been sent"
