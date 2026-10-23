# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Literal, Any, ClassVar, cast
from collections.abc import Iterator
from dataclasses import dataclass

# Third-party modules
import orjson

# NOC modules
from noc.core.msgstream.message import Message
from noc.core.defer import JOBS_STREAM
from noc.core.mx import (
    MessageType,
    MX_JOB_HANDLER,
    MX_DISABLE_MUTATIONS,
    NOTIFICATION_METHODS,
    MX_NOTIFICATION_METHOD,
    MX_NOTIFICATION_GROUP_ID,
    MX_WATCH_FOR_ID,
    MX_TO,
    MX_FWD_ROUTER,
)
from noc.config import config
from noc.main.models.handler import Handler

logger = logging.getLogger(__name__)


DROP = ""
PASS = "<pass>"
DUMP = "<dump>"
FWD = "<fwd>"
ACTION_TYPES: dict[str, type["Action"]] = {}


@dataclass
class HeaderItem:
    header: str
    value: str


@dataclass
class ActionCfg:
    type: Literal["stream", "notification_group", "drop", "job"]
    stream: str | None = None
    notification_group: str | None = None
    render_template: str | None = None
    headers: list[HeaderItem] | None = None


class ActionBase(type):
    def __new__(
        mcs: "type[ActionBase]", name: str, bases: tuple[type[Any], ...], attrs: dict[str, Any]
    ) -> type["Action"]:
        global ACTION_TYPES
        cls = cast(type["Action"], type.__new__(mcs, name, bases, attrs))
        name = getattr(cls, "name", None)
        if name:
            ACTION_TYPES[name] = cls
        return cls


class Action(metaclass=ActionBase):
    name: ClassVar[str]

    def __init__(self, cfg: ActionCfg) -> None:
        self.headers: dict[str, bytes] = {h.header: h.value.encode() for h in cfg.headers or []}

    @classmethod
    def from_data(cls, data):
        global ACTION_TYPES

        action = ACTION_TYPES[data["action"]]
        headers = [HeaderItem(**h) for h in data.get("headers", [])]
        headers += action.get_headers(data) or []
        return action(
            ActionCfg(
                type=data["action"],
                stream=data.get("stream"),
                notification_group=data.get("notification_group"),
                render_template=data.get("render_template"),
                headers=headers,
            )
        )

    @classmethod
    def get_headers(cls, data) -> list[HeaderItem]:
        """Parse internal headers"""

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        raise NotImplementedError


class DropAction(Action):
    name = "drop"

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        yield DROP, {}, msg.value


class DumpAction(Action):
    name = "dump"

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        yield DUMP, {}, msg.value


class StreamAction(Action):
    name = "stream"

    def __init__(self, cfg: ActionCfg) -> None:
        super().__init__(cfg)
        self.stream: str = cfg.stream

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        yield self.stream, self.headers, msg.value


class NotificationAction(Action):
    name = "notification"

    def __init__(self, cfg: ActionCfg) -> None:
        super().__init__(cfg)

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        if MX_NOTIFICATION_METHOD not in msg.headers:
            # Processed send notification
            logger.error("Notification without Method set. Skipping...")
            return
        yield (
            NOTIFICATION_METHODS[msg.headers[MX_NOTIFICATION_METHOD].decode()].decode(),
            msg.headers,
            msg.value,
        )


class MetricAction(Action):
    name = "metrics"

    def __init__(self, cfg: ActionCfg) -> None:
        super().__init__(cfg)
        self.stream: str = cfg.stream
        self.mx_metrics_scopes = {}
        self.load_handlers()

    def load_handlers(self):
        from noc.main.models.metricstream import MetricStream

        for mss in MetricStream.objects.filter():
            if mss.is_active and mss.scope.table_name in set(config.message.enable_metric_scopes):
                self.mx_metrics_scopes[mss.scope.table_name.encode()] = mss.to_mx

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        yield self.stream, self.headers, msg.value


class JobAction(Action):
    name = "job"

    @classmethod
    def get_headers(cls, data):
        """Use transmute handler as"""
        if "transmute_handler" not in data:
            return []
        h = Handler.get_by_id(data["transmute_handler"])
        if h:
            return [HeaderItem(header=MX_JOB_HANDLER, value=h.handler)]
        return []

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        if MX_JOB_HANDLER in self.headers:
            handler = self.headers[MX_JOB_HANDLER]
        elif MX_JOB_HANDLER in msg.headers:
            handler = msg.headers[MX_JOB_HANDLER]
        else:
            return
        if msg.value:
            kw = orjson.loads(msg.value) or {}
        else:
            kw = {}
        yield (
            JOBS_STREAM,
            {MX_DISABLE_MUTATIONS: b""},
            [{"handler": handler.decode(), "kwargs": kw}],
        )
        yield DROP, {}, msg.value


class MessageAction(Action):
    name = "message"

    def __init__(self, cfg: ActionCfg) -> None:
        super().__init__(cfg)
        self.ng: str | None = cfg.notification_group
        self.rt: int | None = cfg.render_template

    def get_notification_group(self, ng: bytes | None):
        from noc.main.models.notificationgroup import NotificationGroup

        if ng:
            return NotificationGroup.get_by_id(int(ng.decode()))
        if not self.ng:
            return None
        return NotificationGroup.get_by_id(int(self.ng))

    def register_escalation(self):
        """Register Notification escalation"""

    def render_template(
        self,
        message_type: MessageType,
        msg: Message,
        language: str | None = None,
        notification_group: Any | None = None,
    ) -> dict[str, str] | None:
        """
        Render Body from template
        Args:
            message_type: Message Type code
            msg: Message
            language: Language Code
            notification_group: Subject Tag
        """
        from noc.main.models.template import Template

        if self.rt:
            template = Template.get_by_id(self.rt)
        elif notification_group:
            template = notification_group.get_effective_template(message_type, language=language)
        else:
            template = Template.get_by_message_type(message_type, language=language)
        if not template:
            # logger.warning("Not template for message type: %s", message_type)
            return None
        ctx = orjson.loads(msg.value)
        try:
            return {"subject": template.render_subject(**ctx), "body": template.render_body(**ctx)}
        except TypeError as e:
            logger.error("Can't Render Template: %s", e)
            return None

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], bytes]]:
        """"""
        ng = self.get_notification_group(msg.headers.get(MX_NOTIFICATION_GROUP_ID))
        if not ng:
            logger.error("Unknown Notification Group: %s", msg.headers[MX_NOTIFICATION_GROUP_ID])
            return
        obj = None
        if MX_WATCH_FOR_ID in msg.headers:
            obj = msg.headers[MX_WATCH_FOR_ID].decode()[2:]
        ts = datetime.datetime.now()
        message_type = MessageType(message_type.decode())
        body: dict[str, Any] | None = None
        for c in ng.get_active_contacts(obj, ts=ts):
            body = body or self.render_template(
                message_type, msg, c.language, notification_group=ng
            )
            if not body:
                logger.warning("Uknown template for message type: %s", message_type)
                break
            if c.title_tag:
                body = {
                    "subject": f"{c.title_tag} {body['subject']}",
                    "body": body["body"],
                }
            headers = {
                MX_TO: c.contact.encode(),
                MX_NOTIFICATION_METHOD: c.method.encode(),
            }
            if c.route:
                headers[MX_FWD_ROUTER] = str(c.route).encode()
                yield FWD, headers, body
            else:
                yield NOTIFICATION_METHODS[c.method].decode(), headers, body
