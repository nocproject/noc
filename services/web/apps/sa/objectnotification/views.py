# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.objectnotification application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.sa.models.objectnotification import ObjectNotification


class ObjectNotificationApplication(ExtModelApplication):
    """
    ObjectNotification application
    """
    title = _("Object Notification")
    menu = [_("Setup"), _("Object Notification")]
    model = ObjectNotification
