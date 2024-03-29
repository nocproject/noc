# ---------------------------------------------------------------------
# main.notificationgroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.main.models.notificationgroup import (
    NotificationGroup,
    NotificationGroupUser,
    NotificationGroupOther,
)
from noc.services.web.base.modelinline import ModelInline
from noc.sa.interfaces.base import ListOfParameter, ModelParameter, UnicodeParameter
from noc.core.translation import ugettext as _


class NotificationGroupApplication(ExtModelApplication):
    """
    NotificationGroup application
    """

    title = _("Notification Group")
    menu = [_("Setup"), _("Notification Groups")]
    model = NotificationGroup
    glyph = "envelope-o"

    users = ModelInline(NotificationGroupUser)
    other = ModelInline(NotificationGroupOther)

    @view(
        url="^actions/test/$",
        method=["POST"],
        access="update",
        api=True,
        validate={
            "ids": ListOfParameter(element=ModelParameter(NotificationGroup)),
            "subject": UnicodeParameter(),
            "body": UnicodeParameter(),
        },
    )
    def api_action_test(self, request, ids, subject, body):
        for g in ids:
            g.notify(subject=subject, body=body)
        return "Notification message has been sent"
