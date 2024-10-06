# ---------------------------------------------------------------------
# main.notificationgroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.aaa.models.user import User
from noc.aaa.models.group import Group
from noc.main.models.notificationgroup import (
    NotificationGroup,
    NotificationGroupUserSubscription,
)
from noc.services.web.base.modelinline import ModelInline
from noc.sa.interfaces.base import ListOfParameter, ModelParameter, UnicodeParameter
from noc.core.translation import ugettext as _


class NotificationGroupApplication(ExtModelApplication):
    """
    NotificationGroup application
    """

    title = _("Notification Group")
    menu = [_("Notification Groups")]
    model = NotificationGroup
    glyph = "envelope-o"

    users = ModelInline(NotificationGroupUserSubscription)

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

    def instance_to_dict(self, o, fields=None):
        r = super().instance_to_dict(o, fields=fields)
        ss = []
        for ss in r.get("subscription_settings", []):
            if ss["user"]:
                u = User.get_by_id(ss["user"])
                ss["user__label"] = u.username
            if ss["group"]:
                g = Group.get_by_id(ss["group"])
                ss["group__label"] = g.name
        return r
