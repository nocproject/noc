# ----------------------------------------------------------------------
# Route
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from typing import (
    Iterator,
    Callable,
    Any,
    Literal,
    Iterable,
)
from dataclasses import dataclass

# Third-party modules
from jinja2 import Template as JTemplate
import orjson

# NOC modules
from noc.core.msgstream.message import Message
from noc.core.matcher import build_matcher
from noc.core.defer import JOBS_STREAM
from noc.core.mx import (
    MX_H_VALUE_SPLITTER,
    MX_NOTIFICATION_METHOD,
    MX_NOTIFICATION_GROUP_ID,
    MX_LABELS,
    MX_RESOURCE_GROUPS,
    MX_JOB_HANDLER,
    MX_DISABLE_MUTATIONS,
    MX_REMOTE_SYSTEMS,
    MX_FWD_ROUTER,
    MessageType,
    MessageMeta,
)
from .action import Action, NotificationAction, MessageAction, ActionCfg, JobAction, HeaderItem, FWD

T_BODY = bytes | Any


@dataclass
class RenderTemplate:
    subject_template: JTemplate
    body_template: JTemplate

    def render_body(self, ctx: dict[str, Any]) -> bytes:
        return orjson.dumps(
            {
                "subject": self.subject_template.render(**ctx),
                "body": self.body_template.render(**ctx),
            }
        )


@dataclass
class TransmuteTemplate:
    template: JTemplate

    def render_body(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return orjson.loads(self.template.render(**ctx).encode())


@dataclass
class HeaderMatchItem:
    header: str
    op: Literal["==", "!=", "regex"]
    value: str

    def __str__(self) -> str:
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
class MatchItem:
    labels: list[str] | None = None
    exclude_labels: list[str] | None = None
    administrative_domain: list[int] | None = None
    resource_groups: list[str] | None = None
    remote_systems: list[str] | None = None
    profile: str | None = None
    headers: list[HeaderMatchItem] | None = None

    @classmethod
    def from_data(cls, data: list[dict[str, Any]]) -> list["MatchItem"]:
        r = []
        for match in data:
            r += [
                MatchItem(
                    labels=match.get(MessageMeta.LABELS.value),
                    exclude_labels=match.get("exclude_labels"),
                    administrative_domain=match.get(MessageMeta.ADM_DOMAIN.value),
                    resource_groups=match.get(MessageMeta.GROUPS.value),
                    profile=match.get(MessageMeta.PROFILE.value),
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
            if MessageMeta.LABELS in r:
                r[MessageMeta.LABELS] |= {
                    "$all_ne": frozenset(ll.encode() for ll in self.exclude_labels)
                }
            else:
                r[MessageMeta.LABELS] = {
                    "$all_ne": frozenset(ll.encode() for ll in self.exclude_labels)
                }
        if self.resource_groups:
            r[MessageMeta.GROUPS] = {"$all": frozenset(x.encode() for x in self.resource_groups)}
        if self.administrative_domain:
            r[MessageMeta.ADM_DOMAIN.config.header] = {
                "$in": frozenset(str(ad).encode() for ad in self.administrative_domain),
            }
        if self.remote_systems:
            r[MessageMeta.REMOTE_SYSTEMS] = {
                "$all": frozenset(x.encode() for x in self.remote_systems)
            }
        if self.profile:
            r[MessageMeta.PROFILE.config.header] = str(self.profile).encode()
        if not self.headers:
            return r
        for h in self.headers:
            if h.op == "regex":
                r[h.header] = {"$regex": re.compile(h.value.encode())}
            elif h.op == "!=":
                r[h.header] = {"$ne": h.value.encode()}
            else:
                r[h.header] = h.value.encode()
        return r


class Route:
    """
    Route Notification. Contains condition and action.
    If condition is matched - do action
    """

    MX_H_VALUE_SPLITTER = MX_H_VALUE_SPLITTER.encode()

    def __init__(
        self, name: str, r_type: str, order: int, telemetry_sample: int | None = None
    ) -> None:
        self.name = name
        self.type: frozenset[bytes] = (
            frozenset([r_type.encode()])
            if isinstance(r_type, str)
            else frozenset(x.encode() for x in r_type)
        )
        self.order = order
        self.telemetry_sample = telemetry_sample or 0
        self.match_co: Callable[[dict[str, Any]], bool] | None = None  # Code object for matcher
        self.actions: list[Action] = []
        self.transmute_handler: Callable[[dict[str, bytes], T_BODY], T_BODY] | None = None
        self.transmute_template: TransmuteTemplate | None = None

    def __str__(self) -> str:
        return f"{self.name} ({self.type}, {self.order}): {self.actions}"

    def __repr__(self) -> str:
        return f"{self.name} ({self.type}, {self.order}): {self.actions}"

    @property
    def m_types(self) -> frozenset[bytes]:
        return self.type

    def get_match_ctx(self, msg: Message) -> dict[MessageMeta, Any]:
        ctx = {}
        if msg.headers.get(MX_LABELS):
            ctx[MessageMeta.LABELS] = frozenset(
                msg.headers[MX_LABELS].split(self.MX_H_VALUE_SPLITTER)
            )
        if msg.headers.get(MX_RESOURCE_GROUPS):
            ctx[MessageMeta.GROUPS] = frozenset(
                msg.headers[MX_RESOURCE_GROUPS].split(self.MX_H_VALUE_SPLITTER)
            )
        if msg.headers.get(MX_REMOTE_SYSTEMS):
            ctx[MessageMeta.REMOTE_SYSTEMS] = frozenset(
                msg.headers[MX_REMOTE_SYSTEMS].split(self.MX_H_VALUE_SPLITTER)
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

    def transmute(self, headers: dict[str, bytes], data: T_BODY) -> bytes | dict[str, Any]:
        """
        Transmute message body and apply template
        Attrs:
            headers: Message Headers
            data: Message Body
        """
        if MX_DISABLE_MUTATIONS in headers:
            return data
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
    ) -> Iterator[tuple[str, dict[str, bytes], T_BODY]]:
        """
        Iterate over available actions

        :return: Stream name or empty string, dict of headers
        """
        for a in self.actions:
            yield from a.iter_action(msg, message_type)

    def set_type(self, r_type: str | frozenset[bytes]):
        if isinstance(r_type, str):
            self.type = frozenset([r_type.encode()])
        else:
            self.type = frozenset(x for x in r_type)

    def set_order(self, order: int):
        self.order = order

    def is_differ(self, data) -> bool:
        """

        :return:
        """
        return True

    @classmethod
    def get_matcher(cls, match) -> Callable[[dict[str, Any]], bool] | None:
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

    def iter_route(self) -> Iterable["Route"]:
        yield self


class DefaultNotificationRoute(Route):
    """
    Default Route for Notification Message
    Route by Notification-Channel message header
    """

    MX_METRIC = MessageType.METRICS.value.encode()

    def __init__(self) -> None:
        super().__init__(name="default", r_type="*", order=-1)
        self.notification_action = NotificationAction(ActionCfg("notification_group"))
        self.message_action = MessageAction(ActionCfg("notification_group"))

    def is_match(self, msg: Message, message_type: bytes) -> bool:
        if message_type == self.MX_METRIC:
            return False
        if MX_NOTIFICATION_METHOD in msg.headers:
            return True
        return MX_NOTIFICATION_GROUP_ID in msg.headers

    def transmute(self, headers: dict[str, bytes], data: bytes) -> bytes | dict[str, Any]:
        return data

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], T_BODY]]:
        if MX_NOTIFICATION_GROUP_ID in msg.headers:
            yield from self.message_action.iter_action(msg, message_type)
        elif MX_FWD_ROUTER in msg.headers:
            yield FWD, msg.headers, msg.value
        else:
            yield from self.notification_action.iter_action(msg, message_type)


class DefaultJobRoute(Route):
    """
    Default Router for Job Request
    Route request to worker
    """

    MX_JOB = MessageType.JOB.value.encode()

    def __init__(self) -> None:
        super().__init__(name="jobs", r_type="job", order=999)
        self.job_action = JobAction(ActionCfg("job", stream=JOBS_STREAM))

    def is_match(self, msg: Message, message_type: bytes) -> bool:
        return message_type == self.MX_JOB and MX_JOB_HANDLER in msg.headers

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], T_BODY]]:
        yield from self.job_action.iter_action(msg, message_type)


class DefaultETLEventRoute(Route):
    """
    Default Router for Job Request
    Route request to worker
    """

    MX_JOB = MessageType.ETL_PUSH.value.encode()
    DEFAULT_HANDLER = "noc.main.models.remotesystem.processed_remote_event"

    def __init__(self) -> None:
        super().__init__(name="etl_jobs", r_type="*", order=999)
        self.job_action = JobAction(
            ActionCfg(
                "job",
                stream=JOBS_STREAM,
                headers=[HeaderItem(header=MX_JOB_HANDLER, value=self.DEFAULT_HANDLER)],
            ),
        )

    def is_match(self, msg: Message, message_type: bytes) -> bool:
        return message_type == self.MX_JOB and MX_REMOTE_SYSTEMS in msg.headers

    def iter_action(
        self, msg: Message, message_type: bytes
    ) -> Iterator[tuple[str, dict[str, bytes], T_BODY]]:
        yield from self.job_action.iter_action(msg, message_type)
