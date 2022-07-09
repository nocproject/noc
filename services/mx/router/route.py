# ----------------------------------------------------------------------
# Route
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, Dict, List, Iterator, Callable, Union, Any, Optional, DefaultDict
from dataclasses import dataclass
from collections import defaultdict

# Third-party modules
from jinja2 import Template
import orjson

# NOC modules
from noc.core.liftbridge.message import Message
from noc.core.comp import smart_bytes
from noc.core.mx import MX_LABELS, MX_H_VALUE_SPLITTER, MX_ADMINISTRATIVE_DOMAIN_ID
from noc.main.models.messageroute import MessageRoute
from .action import Action

T_BODY = Union[bytes, Any]


@dataclass
class RenderTemplate(object):
    subject_template: Template
    body_template: Template

    def render_body(self, ctx: Dict[str, Any]) -> bytes:
        return orjson.dumps(
            {
                "subject": self.subject_template.render(**ctx),
                "body": self.body_template.render(**ctx),
            }
        )


class Route(object):
    def __init__(self, name: str):
        self.name = name
        self.match_co: str = ""  # Code object for matcher
        self.actions: List[Action] = []
        self.transmute_handler: Optional[Callable[[Dict[str, bytes], T_BODY], T_BODY]] = None
        self.render_template: Optional[RenderTemplate] = None

    def is_match(self, msg: Message) -> bool:
        """
        Check if the route is applicable for messages

        :param msg:
        :return:
        """
        ctx = {"headers": msg.headers, "labels": set()}
        if MX_LABELS in msg.headers:
            ctx["labels"] = set(msg.headers[MX_LABELS].split(smart_bytes(MX_H_VALUE_SPLITTER)))
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
        if self.render_template:
            if isinstance(data, bytes):
                data = orjson.loads(data)
            ctx = {"headers": headers, **data}
            return self.render_template.render_body(**ctx)
        return data

    def iter_action(self, msg: Message) -> Iterator[Tuple[str, Dict[str, bytes]]]:
        """
        Iterate over available actions

        :return: Stream name or empty string, dict of headers
        """
        for a in self.actions:
            yield from a.iter_action(msg)

    @classmethod
    def from_route(cls, route: MessageRoute) -> "Route":
        """
        Build Route from database config
        :param route:
        :return:
        """
        r = Route(route.name)
        expr = []
        # Compile match section
        match_eq: DefaultDict[str, List[bytes]] = defaultdict(list)
        match_re: DefaultDict[str, List[bytes]] = defaultdict(list)
        match_ne: List[Tuple[str, bytes]] = []
        for match in route.match:
            if match.labels:
                expr += [f"{set(smart_bytes(ll) for ll in match.labels)!r}.intersection(labels)"]
            if match.exclude_labels:
                expr += [
                    f"not {set(smart_bytes(ll) for ll in match.exclude_labels)!r}.intersection(labels)"
                ]
            if match.administrative_domain:
                expr += [
                    f"headers[{MX_ADMINISTRATIVE_DOMAIN_ID!r}] == {match.administrative_domain.id}"
                ]
            for h_match in match.headers_match:
                if h_match.is_eq:
                    match_eq[h_match.header] += [smart_bytes(h_match.value)]
                elif h_match.is_ne:
                    match_ne += [(h_match.header, smart_bytes(h_match.value))]
                elif h_match.is_re:
                    match_re[h_match.header] += [smart_bytes(h_match.value)]
        # Expression for ==
        for header in match_eq:
            if len(match_eq[header]) == 1:
                # ==
                expr += ["headers[%r] == %r" % (header, match_eq[header][0])]
            else:
                # in
                expr += [
                    "headers[%r] in (%s)" % (header, ", ".join("%r" % x for x in match_eq[header]))
                ]
        # Expression for !=
        for header, value in match_ne:
            expr += ["headers[%r] != %r" % (header, smart_bytes(value))]
        # Expression for regex
        # @todo
        # Compile matching code
        if expr:
            cond_code = " and ".join(expr)
        else:
            cond_code = "True"
        r.match_co = compile(cond_code, "<string>", "eval")
        # Compile transmute part
        # r.transmutations = [Transmutation.from_transmute(t) for t in route.transmute]
        r.transmute_handler = route.transmute_handler
        if route.transmute_template:
            r.render_template = RenderTemplate(
                subject_template=route.transmute_template.subject,
                body_template=route.transmute_template.body,
            )
        # Compile action part
        r.actions = [Action.from_action(route)]
        return r
