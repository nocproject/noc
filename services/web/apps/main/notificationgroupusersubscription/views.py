# ---------------------------------------------------------------------
# main.notificationgroupusersubscription application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.main.models.notificationgroup import NotificationGroupUserSubscription
from noc.core.translation import ugettext as _


class NotificationGroupUserSubscriptionApplication(ExtModelApplication):
    """
    NotificationGroupUserSubscription application
    """

    title = _("Notification User Subscriptions")
    menu = [_("Notification User Subscriptions")]
    model = NotificationGroupUserSubscription
