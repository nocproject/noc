# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Type, Tuple, Dict, Iterator, Literal, Optional, List
from dataclasses import dataclass

# Third-party modules
import orjson

# NOC modules
from noc.core.liftbridge.message import Message
from noc.core.comp import DEFAULT_ENCODING
from noc.core.mx import MX_MESSAGE_TYPE, NOTIFICATION_METHODS, MX_METRICS_SCOPE
from noc.config import config


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

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        raise NotImplementedError


class DropAction(Action):
    name = "drop"

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield DROP, {}, msg.value


class DumpAction(Action):
    name = "dump"

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield DUMP, {}, msg.value


class StreamAction(Action):
    name = "stream"

    def __init__(self, cfg: ActionCfg):
        super().__init__(cfg)
        self.stream: str = cfg.stream

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        yield self.stream, self.headers, msg.value


class NotificationAction(Action):
    name = "notification"

    def __init__(self, cfg: ActionCfg):
        from noc.main.models.notificationgroup import NotificationGroup
        from noc.main.models.template import Template

        super().__init__(cfg)
        self.ng: NotificationGroup = NotificationGroup.get_by_id(cfg.notification_group)
        self.rt: Template = Template.get_by_id(cfg.render_template)

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        mt = msg.headers.get(MX_MESSAGE_TYPE).decode(DEFAULT_ENCODING)
        body = self.ng.render_message(mt, orjson.loads(msg.value), self.rt)
        for method, header, render_template in self.ng.iter_actions():
            yield NOTIFICATION_METHODS[method], header, self.ng.render_message(
                mt, orjson.loads(msg.value), render_template
            ) if render_template else body


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

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes], bytes]]:
        table = msg.headers.get(MX_METRICS_SCOPE)
        if table not in self.mx_metrics_scopes:
            return
        yield self.stream, self.headers, [
            self.mx_metrics_scopes[table](orjson.loads(v)) for v in msg.value.split(b"\n")
        ]
