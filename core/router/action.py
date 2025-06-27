# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Type, Tuple, Dict, Iterator, Literal, Optional, List
from dataclasses import dataclass

# Third-party modules
import orjson

# NOC modules
from noc.core.msgstream.message import Message
from noc.core.comp import DEFAULT_ENCODING
from noc.core.mx import (
    MessageType,
    NOTIFICATION_METHODS,
    MX_NOTIFICATION_METHOD,
    MX_NOTIFICATION_DELAY,
    MX_NOTIFICATION_GROUP_ID,
    MX_WATCH_FOR_ID,
    MX_TO,
    MessageMeta,
)
from noc.config import config

logger = logging.getLogger(__name__)


DROP = ""
PASS = "<pass>"
DUMP = "<dump>"
ACTION_TYPES: Dict[str, Type["Action"]] = {}


@dataclass
class HeaderItem(object):
    header: str
    value: str


@dataclass
class ActionCfg(object):
    type: Literal["stream", "notification_group", "drop"]
    stream: Optional[str] = None
    notification_group: Optional[str] = None
    render_template: Optional[str] = None
    headers: Optional[List[HeaderItem]] = None


class ActionBase(type):
    def __new__(mcs, name, bases, attrs):
        global ACTION_TYPES
        cls = type.__new__(mcs, name, bases, attrs)
        name = getattr(cls, "name", None)
        if name:
            ACTION_TYPES[name] = cls
        return cls


class Action(object, metaclass=ActionBase):
    name: str

    def __init__(self, cfg: ActionCfg):
        self.headers: Dict[str, bytes] = {
            h.header: h.value.encode(encoding=DEFAULT_ENCODING) for h in cfg.headers or []
        }

    @classmethod
    def from_data(cls, data):
        global ACTION_TYPES

        return ACTION_TYPES[data["action"]](
            ActionCfg(
                type=data["action"],
                stream=data.get("stream"),
                notification_group=data.get("notification_group"),
                render_template=data.get("render_template"),
                headers=[HeaderItem(**h) for h in data.get("headers", [])],
            )
        )

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        raise NotImplementedError


class DropAction(Action):
    name = "drop"

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield DROP, {}, msg.value


class DumpAction(Action):
    name = "dump"

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield DUMP, {}, msg.value


class StreamAction(Action):
    name = "stream"

    def __init__(self, cfg: ActionCfg):
        super().__init__(cfg)
        self.stream: str = cfg.stream

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield self.stream, self.headers, msg.value


class NotificationAction(Action):
    name = "notification"

    def __init__(self, cfg: ActionCfg):
        super().__init__(cfg)
        self.ng: Optional[str] = cfg.notification_group
        self.rt: Optional[int] = cfg.render_template

    def get_notification_group(self, ng: Optional[bytes]):
        from noc.main.models.notificationgroup import NotificationGroup

        if ng:
            return NotificationGroup.get_by_id(int(ng.decode()))
        elif not self.ng:
            return
        return NotificationGroup.get_by_id(self.ng)

    def register_escalation(self):
        """Register Notification escalation"""

    def render_template(
        self, message_type: bytes, msg: Message, language: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Render Body from template
        Args:
            message_type: Message Type code
            msg: Message
            language: Language Code
            tag: Subject Tag
        """
        from noc.main.models.template import Template

        if not self.rt:
            mt = MessageType(message_type.decode())
            template = Template.get_by_message_type(mt)
        else:
            template = Template.get_by_id(self.rt)
        if not template:
            # logger.warning("Not template for message type: %s", message_type)
            return None
        ctx = orjson.loads(msg.value)
        return {"subject": template.render_subject(**ctx), "body": template.render_body(**ctx)}

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        """"""
        # if MX_NOTIFICATION_METHOD in msg.headers:
        #     yield NOTIFICATION_METHODS[msg.headers[MX_NOTIFICATION_METHOD].decode()], {}, msg.value
        ng = self.get_notification_group(msg.headers.get(MX_NOTIFICATION_GROUP_ID))
        if not ng:
            logger.error("Unknown Notification Group: %s", msg.headers[MX_NOTIFICATION_GROUP_ID])
            return
        try:
            body = self.render_template(message_type, msg)
        except TypeError as e:
            logger.error("Can't Render Template: %s", e)
            return
        obj = None
        if MX_WATCH_FOR_ID in msg.headers:
            obj = msg.headers[MX_WATCH_FOR_ID].decode()[2:]
        ts = datetime.datetime.now()
        for c in ng.get_active_contacts(obj, ts=ts):
            if c.title_tag:
                body = {
                    "subject": f'{c.title_tag} {body["subject"]}',
                    "body": body["body"],
                }
            yield NOTIFICATION_METHODS[c.method].decode(), {
                MX_TO: c.contact.encode(encoding=DEFAULT_ENCODING)
            }, body

    def iter_action_old(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        #
        try:
            body = self.render_template(message_type, msg)
        except TypeError as e:
            print("Cant Render Template: %s" % e)
            return
        if not body:
            # Unknown template
            # print("Unknown Template")
            return
        if MX_NOTIFICATION_DELAY in msg.headers:
            ...
        if MX_NOTIFICATION_METHOD in msg.headers:
            yield NOTIFICATION_METHODS[msg.headers[MX_NOTIFICATION_METHOD].decode()], {}, msg.value
        ng = self.get_notification_group(msg.headers.get(MX_NOTIFICATION_GROUP_ID))
        if not ng:
            # print(f"Unknown Notification Group: {MX_NOTIFICATION_GROUP_ID}")
            return
        for method, headers, render_template in ng.iter_actions(
            message_type.decode(),
            (
                {MessageMeta.WATCH_FOR: msg.headers[MX_WATCH_FOR_ID].decode()}
                if MX_WATCH_FOR_ID in msg.headers
                else {}
            ),
        ):
            yield NOTIFICATION_METHODS[method].decode(), headers, body


class MetricAction(Action):
    name = "metrics"

    def __init__(self, cfg: ActionCfg):
        super().__init__(cfg)
        self.stream: str = cfg.stream
        self.mx_metrics_scopes = {}
        self.load_handlers()

    def load_handlers(self):
        from noc.main.models.metricstream import MetricStream

        for mss in MetricStream.objects.filter():
            if mss.is_active and mss.scope.table_name in set(config.message.enable_metric_scopes):
                self.mx_metrics_scopes[mss.scope.table_name.encode(DEFAULT_ENCODING)] = mss.to_mx

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield self.stream, self.headers, msg.value
