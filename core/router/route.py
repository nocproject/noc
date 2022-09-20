# ----------------------------------------------------------------------
# Route
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, Dict, List, Iterator, Callable, Union, Any, Optional, DefaultDict, Literal
from dataclasses import dataclass
from collections import defaultdict

# Third-party modules
from jinja2 import Template as JTemplate
import orjson

# NOC modules
from noc.core.liftbridge.message import Message
from noc.core.comp import DEFAULT_ENCODING
from noc.core.mx import (
    MX_LABELS,
    MX_H_VALUE_SPLITTER,
    MX_ADMINISTRATIVE_DOMAIN_ID,
    MX_NOTIFICATION_CHANNEL,
    MX_NOTIFICATION,
    MX_MESSAGE_TYPE,
    NOTIFICATION_METHODS,
)
from .action import Action

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
    administrative_domain: Optional[int] = None
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
                    headers=[
                        HeaderMatchItem(header=h["header"], op=h["op"], value=h["value"])
                        for h in match["headers"]
                    ],
                )
            ]
        return r


class Route(object):
    """
    Route Notification. Contains condition and action.
    If condition is matched - do action
    """

    def __init__(self, name: str, r_type: str, order: int):
        self.name = name
        self.type = r_type
        self.order = order
        self.match_co: str = ""  # Code object for matcher
        self.actions: List[Action] = []
        self.transmute_handler: Optional[Callable[[Dict[str, bytes], T_BODY], T_BODY]] = None
        self.transmute_template: Optional[TransmuteTemplate] = None

    def is_match(self, msg: Message) -> bool:
        """
        Check if the route is applicable for messages

        :param msg:
        :return:
        """
        ctx = {"headers": msg.headers, "labels": set()}
        if MX_LABELS in msg.headers:
            ctx["labels"] = set(
                msg.headers[MX_LABELS].split(MX_H_VALUE_SPLITTER.encode(encoding=DEFAULT_ENCODING))
            )
        return eval(self.match_co, ctx)

    def transmute(self, headers: Dict[str, bytes], data: bytes) -> Union[bytes, Dict[str, Any]]:
        """
        Transmute message body and apply template
        :param headers:
        :param data:
        :return:
        """
        if self.transmute_handler:
            data = self.transmute_handler(headers, data)
        elif self.transmute_template:
            if isinstance(data, bytes):
                data = orjson.loads(data)
            ctx = {"headers": headers, **data}
            data = self.transmute_template.render_body(ctx)
        return data

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        """
        Iterate over available actions

        :return: Stream name or empty string, dict of headers
        """
        for a in self.actions:
            yield from a.iter_action(msg)

    def set_type(self, r_type: str):
        self.type = r_type.encode(encoding=DEFAULT_ENCODING)

    def set_order(self, order: int):
        self.order = order

    def is_differ(self, data) -> bool:
        """

        :param data:
        :return:
        """
        return True

    def update(self, data):
        from noc.main.models.template import Template
        from noc.main.models.handler import Handler

        self.match_co = self.compile_match(MatchItem.from_data(data["match"]))
        # Compile transmute part
        # r.transmutations = [Transmutation.from_transmute(t) for t in route.transmute]
        if "transmute_handler" in data:
            self.transmute_handler = Handler.get_by_id(data["transmute_handler"])
        if "transmute_template" in data:
            template = Template.objects.get(id=data["transmute_template"])
            self.transmute_template = TransmuteTemplate(JTemplate(template.body))
        # Compile action part
        self.actions = [Action.from_data(data)]

    @classmethod
    def compile_match(cls, matches: List[MatchItem]):
        expr = []
        # Compile match section
        match_eq: DefaultDict[str, List[bytes]] = defaultdict(list)
        match_re: DefaultDict[str, List[bytes]] = defaultdict(list)
        match_ne: List[Tuple[str, bytes]] = []
        for match in matches:
            if match.labels:
                expr += [
                    f"{set(ll.encode(encoding=DEFAULT_ENCODING) for ll in match.labels)!r}.intersection(labels)"
                ]
            if match.exclude_labels:
                expr += [
                    f"not {set(ll.encode(encoding=DEFAULT_ENCODING) for ll in match.exclude_labels)!r}.intersection(labels)"
                ]
            if match.administrative_domain:
                expr += [
                    f"headers[{MX_ADMINISTRATIVE_DOMAIN_ID!r}] == {match.administrative_domain}"
                ]
            for h_match in match.headers:
                if h_match.is_eq:
                    match_eq[h_match.header] += [h_match.value.encode(encoding=DEFAULT_ENCODING)]
                elif h_match.is_ne:
                    match_ne += [(h_match.header, h_match.value.encode(encoding=DEFAULT_ENCODING))]
                elif h_match.is_re:
                    match_re[h_match.header] += [h_match.value.encode(encoding=DEFAULT_ENCODING)]
        # Expression for ==
        for header in match_eq:
            if len(match_eq[header]) == 1:
                # ==
                expr += [f"headers[{header!r}] == {match_eq[header][0]!r}"]
            else:
                # in
                expr += [
                    f'headers[{header!r}] in ({", ".join("%r" % x for x in match_eq[header])!r})'
                ]
        # Expression for !=
        for header, value in match_ne:
            expr += [f"headers[{header!r}] != {value!r}"]
        # Expression for regex
        # @todo
        # Compile matching code
        if expr:
            cond_code = " and ".join(expr)
        else:
            cond_code = "True"
        return compile(cond_code, "<string>", "eval")

    @classmethod
    def from_data(cls, data) -> "Route":
        """
        Build Route from data config
        :param data:
        :return:
        """
        r = Route(data["name"], data["type"], data["order"])
        r.update(data)
        return r


class DefaultNotificationRoute(Route):
    """
    Default Route for Notification Message
    Route by Notification-Channel message header
    """

    MX_NOTIFICATION_EN = MX_NOTIFICATION.encode(DEFAULT_ENCODING)

    def __init__(self):
        super().__init__(name="default", r_type=MX_NOTIFICATION, order=0)

    def is_match(self, msg: Message) -> bool:
        if (
            MX_NOTIFICATION_CHANNEL in msg.headers
            and msg.headers.get(MX_MESSAGE_TYPE) == self.MX_NOTIFICATION_EN
        ):
            return True
        return False

    def transmute(self, headers: Dict[str, bytes], data: bytes) -> Union[bytes, Dict[str, Any]]:
        return data

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        method = msg.headers.get(MX_NOTIFICATION_CHANNEL).decode(DEFAULT_ENCODING)
        if method not in NOTIFICATION_METHODS:
            # Check available channel for sender
            return
        yield NOTIFICATION_METHODS[method], {}, msg.value
