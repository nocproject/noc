# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.systemnotification application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.main.models import SystemNotification


class SystemNotificationApplication(ExtModelApplication):
    """
    SystemNotification application
    """
    title = _("System Notifications")
    menu = [_("Setup"), _("System Notifications")]
    model = SystemNotification
    query_fields = ["name__icontains"]
