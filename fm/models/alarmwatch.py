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
from mongoengine.fields import EnumField, StringField, BooleanField, DictField, DateTimeField


# Python modules
from noc.core.handler import get_handler
from noc.core.mx import MessageType
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.aaa.models.user import User


class Effect(enum.Enum):
    TT_SYSTEM = "tt_system"
    NOTIFICATION_GROUP = "notification_group"
    SUBSCRIPTION = "subscription"
    HANDLER = "handler"
    ALARM_JOB = "alarm_job"
    SEVERITY = "severity"
    STOP_CLEAR = "stop_clear"
    CLEAR_ALARM = "clear_alarm"
    REWRITE_ALARM_CLASS = "rewrite_ac"


class WatchItem(EmbeddedDocument):
    """
    Attributes:
        effect: Watch Effect
        key: Id for action Instance
        once: Run only once
        immediate: Execute in runtime, not call later
        clear_only: Execute when alarm clear
        after: Execute after deadline
        args: Addition options for run
    """

    meta = {"strict": False, "auto_create_index": False}

    effect: Effect = EnumField(Effect, required=True)
    key: str = StringField(required=True)
    once: bool = BooleanField(default=True)
    immediate: bool = BooleanField(default=False)
    clear_only: bool = BooleanField(default=False)
    after = DateTimeField(required=False)
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
            template = Template.get_by_id(int(template))
        r |= alarm.get_message_body(is_clear=is_clear, template=template)
        return r

    def run(self, alarm, is_clear: bool = False, dry_run: bool = False):
        match self.effect:
            case Effect.TT_SYSTEM:
                AlarmEscalation.watch_alarm(**self.get_args(alarm, is_clear))
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
            case Effect.ALARM_JOB:
                alarm.refresh_job(is_clear, job_id=self.key)
            case Effect.CLEAR_ALARM:
                # To Last Action
                if not is_clear:
                    # Condition deny recursion
                    alarm.clear_alarm("Clear alarm by DeadLine", dry_run=dry_run)
