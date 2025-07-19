# ---------------------------------------------------------------------
# AlarmWatch model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import enum

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EnumField, StringField, BooleanField, DictField


# Python modules
from noc.models import get_model
from noc.core.handler import get_handler
from noc.core.mx import MessageType
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.aaa.models.user import User


class Effect(enum.Enum):
    TT_SYSTEM = "tt_system"
    NOTIFICATION_GROUP = "notification_group"
    SUBSCRIPTION = "subscription"
    HANDLER = "handler"


class WatchItem(EmbeddedDocument):
    """
    Attributes:
        effect: Watch Effect
        key: Id for action Instance
        once: Run only once
        immediate: Execute in runtime, not call later
        clear_only: Execute when alarm clear
        args: Addition options for run
    """

    effect: Effect = EnumField(Effect, required=True)
    key: str = StringField(required=True)
    once: bool = BooleanField(default=True)
    immediate: bool = BooleanField(default=False)
    clear_only: bool = BooleanField(default=False)
    args = DictField(default=dict)

    def __str__(self):
        return f"{self.effect}:{self.key}"

    def get_args(self, alarm, is_clear):
        r = {"alarm": alarm, "is_clear": is_clear}
        if self.args:
            r |= self.args
        if self.effect == Effect.TT_SYSTEM:
            r["tt_id"] = self.key
        template = self.args.get("template")
        if template:
            template = Template.get_by_id(int(self.args["template"]))
        r |= alarm.get_message_body(is_clear=is_clear, template=template)
        return r

    def run(self, alarm, is_clear: bool = False):
        match self.effect:
            case Effect.TT_SYSTEM:
                m = get_model("fm.AlarmEscalation")
                m.watch_alarm(**self.get_args(alarm, is_clear))
            case Effect.NOTIFICATION_GROUP:
                ng = NotificationGroup.get_by_id(int(self.key))
                ng.notify(**self.get_args(alarm, is_clear))
            case Effect.SUBSCRIPTION:
                u = User.get_by_id(int(self.key))
                NotificationGroup.notify_user(
                    u, MessageType.ALARM, **self.get_args(alarm, is_clear)
                )
            case Effect.HANDLER:
                h = get_handler(self.key)
                h(**self.get_args(alarm, is_clear))
