# ----------------------------------------------------------------------
# Route
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from typing import (
    Tuple,
    Dict,
    List,
    Iterator,
    Iterable,
    Callable,
    Union,
    Any,
    Optional,
    Literal,
    FrozenSet,
)
from dataclasses import dataclass

# Third-party modules
from jinja2 import Template as JTemplate
import orjson

# NOC modules
from noc.core.msgstream.message import Message
from noc.core.matcher import build_matcher
from noc.core.comp import DEFAULT_ENCODING
from noc.core.mx import (
    MX_H_VALUE_SPLITTER,
    MX_NOTIFICATION_CHANNEL,
    MX_NOTIFICATION,
    MX_NOTIFICATION_GROUP_ID,
    MX_LABELS,
    MX_RESOURCE_GROUPS,
    MessageType,
    MessageMeta,
)
from .action import Action, NotificationAction, ActionCfg

T_BODY = Union[bytes, Any]


@dataclass
class RenderTemplate(object):
    subject_template: JTemplate
    body_template: JTemplate

    def render_body(self, ctx: Dict[str, Any]) -> bytes:
        return orjson.dumps(
            {
                "subject": self.subject_template.render(**ctx),
                "body": self.body_template.render(**ctx),
            }
        )


@dataclass
class TransmuteTemplate(object):
    template: JTemplate

    def render_body(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        return orjson.loads(self.template.render(**ctx).encode(encoding=DEFAULT_ENCODING))


@dataclass
class HeaderMatchItem(object):
    header: str
    op: Literal["==", "!=", "regex"]
    value: str

    def __str__(self):
        return f"{self.op} {self.header} {self.value}"

    @property
    def is_eq(self) -> bool:
        return self.op == "=="

    @property
    def is_ne(self) -> bool:
        return self.op == "!="

    @property
    def is_re(self) -> bool:
        return self.op == "regex"


@dataclass(frozen=True)
class MatchItem(object):
    labels: Optional[List[str]] = None
    exclude_labels: Optional[List[str]] = None
    administrative_domain: Optional[List[int]] = None
    resource_groups: Optional[List[str]] = None
    profile: Optional[str] = None
    headers: Optional[List[HeaderMatchItem]] = None

    @classmethod
    def from_data(cls, data: List[Dict[str, Any]]) -> List["MatchItem"]:
        r = []
        for match in data:
            r += [
                MatchItem(
                    labels=match["labels"],
                    exclude_labels=match["exclude_labels"],
                    administrative_domain=match.get("administrative_domain"),
                    resource_groups=match.get("resource_groups"),
                    profile=match.get("profile"),
                    headers=[
                        HeaderMatchItem(header=h["header"], op=h["op"], value=h["value"])
                        for h in match["headers"]
                    ],
                )
            ]
        return r

    def get_match_expr(self):
        r = {}
        if self.labels:
            r[MessageMeta.LABELS] = {"$all": frozenset(ll.encode() for ll in self.labels)}
        if self.exclude_labels:
            r[MessageMeta.LABELS] = {"$nin": frozenset(ll.encode() for ll in self.exclude_labels)}
        if self.resource_groups:
            r[MessageMeta.GROUPS] = {"$all": frozenset(x.encode() for x in self.resource_groups)}
        if self.administrative_domain:
            r[MessageMeta.ADM_DOMAIN.config.header] = {
                "$in": frozenset(str(ad).encode() for ad in self.administrative_domain),
            }
        if self.profile:
            r[MessageMeta.PROFILE.config.header] = str(self.profile).encode()
        if not self.headers:
            return r
        for h in self.headers:
            if h.op == "regex":
                r[h.header] = {"$regex": re.compile(h.value.encode(DEFAULT_ENCODING))}
            elif h.op == "!=":
                continue
            else:
                r[h.header.encode()] = h.value.encode(DEFAULT_ENCODING)
        return r


class Route(object):
    """
    Route Notification. Contains condition and action.
    If condition is matched - do action
    """

    MX_H_VALUE_SPLITTER = MX_H_VALUE_SPLITTER.encode(DEFAULT_ENCODING)

    def __init__(self, name: str, r_type: str, order: int, telemetry_sample: Optional[int] = None):
        self.name = name
        self.type: FrozenSet[bytes] = (
            frozenset([r_type.encode()])
            if isinstance(r_type, str)
            else frozenset(x.encode() for x in r_type)
        )
        self.order = order
        self.telemetry_sample = telemetry_sample or 0
        self.match_co: Optional[Callable] = None  # Code object for matcher
        self.actions: List[Action] = []
        self.transmute_handler: Optional[Callable[[Dict[str, bytes], T_BODY], T_BODY]] = None
        self.transmute_template: Optional[TransmuteTemplate] = None

    @property
    def m_types(self) -> FrozenSet[bytes]:
        return self.type

    def get_match_ctx(self, msg: Message) -> Dict[MessageMeta, Any]:
        ctx = {}
        if MX_LABELS in msg.headers and msg.headers[MX_LABELS]:
            ctx[MessageMeta.LABELS] = frozenset(
                msg.headers[MX_LABELS].split(self.MX_H_VALUE_SPLITTER)
            )
        if MX_RESOURCE_GROUPS in msg.headers and msg.headers[MX_RESOURCE_GROUPS]:
            ctx[MessageMeta.GROUPS] = frozenset(
                msg.headers[MX_RESOURCE_GROUPS].split(self.MX_H_VALUE_SPLITTER)
            )
        ctx.update(msg.headers)
        return ctx

    def is_match(self, msg: Message, message_type: bytes) -> bool:
        """
        Check if the route is applicable for messages
        Attrs:
            msg: message for processed
            message_type: Message Type
        """
        if not self.match_co:
            return True
        return self.match_co(self.get_match_ctx(msg))

    def transmute(self, headers: Dict[str, bytes], data: bytes) -> Union[bytes, Dict[str, Any]]:
        """
        Transmute message body and apply template
        Attrs:
            headers: Message Headers
            data: Message Body
        """
        if self.transmute_handler:
            data = self.transmute_handler(headers, data)
        elif self.transmute_template:
            if isinstance(data, bytes):
                data = orjson.loads(data)
            ctx = {"headers": headers, **data}
            data = self.transmute_template.render_body(ctx)
        return data

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        """
        Iterate over available actions

        :return: Stream name or empty string, dict of headers
        """
        for a in self.actions:
            yield from a.iter_action(msg, message_type)

    def set_type(self, r_type: Union[str, FrozenSet[bytes]]):
        if isinstance(r_type, str):
            self.type = frozenset([r_type.encode(encoding=DEFAULT_ENCODING)])
        else:
            self.type = frozenset(x for x in r_type)

    def set_order(self, order: int):
        self.order = order

    def is_differ(self, data) -> bool:
        """

        :param data:
        :return:
        """
        return True

    @classmethod
    def get_matcher(cls, match) -> Optional[Callable]:
        """"""
        expr = []
        for r in MatchItem.from_data(match):
            expr.append(r.get_match_expr())
        if not expr:
            return None
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def update(self, data):
        from noc.main.models.template import Template
        from noc.main.models.handler import Handler

        self.match_co = self.get_matcher(data["match"])
        # Compile transmute part
        # r.transmutations = [Transmutation.from_transmute(t) for t in route.transmute]
        if "transmute_handler" in data:
            h = Handler.get_by_id(data["transmute_handler"])
            self.transmute_handler = h.get_handler() if h else None
        if "transmute_template" in data:
            template = Template.get_by_id(data["transmute_template"])
            self.transmute_template = TransmuteTemplate(JTemplate(template.body))
        # Compile action part
        self.actions = [Action.from_data(data)]

    @classmethod
    def from_data(cls, data) -> "Route":
        """
        Build Route from data config
        Attrs:
            data: Datastream record
        """
        r = Route(data["name"], data["type"], data["order"], data.get("telemetry_sample"))
        r.update(data)
        return r


class DefaultNotificationRoute(Route):
    """
    Default Route for Notification Message
    Route by Notification-Channel message header
    """

    MX_METRIC = MessageType.METRICS.value.encode()

    def __init__(self):
        super().__init__(name="default", r_type="*", order=999)
        self.na = NotificationAction(ActionCfg("notification_group"))

    def is_match(self, msg: Message, message_type: bytes) -> bool:
        if message_type == self.MX_METRIC:
            return False
        elif message_type == MX_NOTIFICATION and MX_NOTIFICATION_CHANNEL in msg.headers:
            return True
        return MX_NOTIFICATION_GROUP_ID in msg.headers

    def transmute(self, headers: Dict[str, bytes], data: bytes) -> Union[bytes, Dict[str, Any]]:
        return data

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        if MX_NOTIFICATION_CHANNEL in msg.headers:
            # Check available channel for sender
            yield msg.headers[MX_NOTIFICATION_CHANNEL].decode(DEFAULT_ENCODING), {}, msg.value
        yield from self.na.iter_action(msg, message_type)
