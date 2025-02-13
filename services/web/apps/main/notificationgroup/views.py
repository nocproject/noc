# ---------------------------------------------------------------------
# main.notificationgroup application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.aaa.models.user import User
from noc.aaa.models.group import Group
from noc.main.models.notificationgroup import NotificationGroup, NOTIFICATION_METHOD_CHOICES
from noc.main.models.timepattern import TimePattern
from noc.sa.interfaces.base import (
    ListOfParameter,
    ModelParameter,
    UnicodeParameter,
    DateTimeParameter,
    StringParameter,
)
from noc.core.translation import ugettext as _


class NotificationGroupApplication(ExtModelApplication):
    """
    NotificationGroup application
    """

    title = _("Notification Group")
    menu = [_("Notification Groups")]
    model = NotificationGroup
    glyph = "envelope-o"

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

    @view(
        url=r"^(?P<group_id>\d+)/change_user_subscription/$",
        validate={
            "user_policy": StringParameter(choices=["D", "W", "A"]),
            "time_pattern": ModelParameter(TimePattern, required=False),
            "expired_at": DateTimeParameter(required=False),
            "title_tag": StringParameter(required=False),
            "preferred_method": StringParameter(
                choices=NOTIFICATION_METHOD_CHOICES, required=False
            ),
        },
        method=["POST"],
        access="update",
        api=True,
    )
    def api_change_user_subscription(
        self,
        request,
        group_id,
        user_policy: Optional[str] = None,
        time_pattern: Optional[TimePattern] = None,
        expired_at: Optional[str] = None,
        title_tag: Optional[str] = None,
        preferred_method: Optional[str] = None,
    ):
        o = self.get_object_or_404(NotificationGroup, pk=int(group_id))
        user = request.user
        if not user:
            return self.response_not_found()
        us = o.get_subscription_by_user(user)
        if expired_at:
            expired_at = datetime.datetime.fromisoformat(expired_at)
        if not us:
            us = o.subscribe(user, expired_at=expired_at)
        if us.time_pattern != time_pattern:
            us.time_pattern = time_pattern
        if us.expired_at != expired_at:
            us.expired_at = expired_at
        if us.policy != user_policy:
            us.policy = user_policy
        if us.title_tag != title_tag:
            us.title_tag = title_tag
        if us.method != preferred_method:
            us.method = preferred_method
        us.save()
        data = {
            "notification_group": str(o.id),
            "notification_group__label": o.name,
            "user_policy": us.policy,
            "time_pattern": us.time_pattern,
            "supress": False,
            "preferred_method": us.method,
            "expired_at": us.expired_at,
            "title_tag": us.title_tag,
            "message_types": [t["message_type"] for t in o.message_types],
        }
        if us.time_pattern:
            data["time_pattern__label"] = us.time_pattern.name
        return data

    def instance_to_dict(self, o, fields=None):
        r = super().instance_to_dict(o, fields=fields)
        r["subscription_settings"] = []
        for ss in o.iter_subscription_settings:
            x = ss.model_dump()
            if ss.user:
                u = User.get_by_id(ss.user)
                x["user__label"] = u.username
            if ss.group:
                g = Group.get_by_id(ss.group)
                x["group__label"] = g.name
            r["subscription_settings"].append(x)
        for ss in r.get("message_types", []):
            ss["message_type__label"] = ss["message_type"]
        return r
