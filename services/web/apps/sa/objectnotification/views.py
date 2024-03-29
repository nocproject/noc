# ---------------------------------------------------------------------
# sa.objectnotification application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.sa.models.objectnotification import ObjectNotification
from noc.core.translation import ugettext as _


class ObjectNotificationApplication(ExtModelApplication):
    """
    ObjectNotification application
    """

    title = _("Object Notification")
    menu = [_("Setup"), _("Object Notification")]
    model = ObjectNotification
