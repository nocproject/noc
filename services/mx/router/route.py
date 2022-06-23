# ----------------------------------------------------------------------
# Route
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Tuple, Dict, List, DefaultDict, Iterator

# NOC modules
from noc.core.liftbridge.message import Message
from noc.core.comp import smart_bytes
from noc.core.mx import MX_LABELS, MX_H_VALUE_SPLITTER
from noc.main.models.messageroute import MessageRoute
from .action import Action
from .transmute import Transmutation


class Route(object):
    def __init__(self, name: str):
        self.name = name
        self.match_co: str = ""  # Code object for matcher
        self.actions: List[Action] = []
        self.transmutations: List[Transmutation] = []

    def is_match(self, msg: Message) -> bool:
        """
        Check if the route is applicable for messages

        :param msg:
        :return:
        """
        headers = msg.headers
        if MX_LABELS in headers:
            headers[MX_LABELS] = headers[MX_LABELS].split(smart_bytes(MX_H_VALUE_SPLITTER))
        return eval(self.match_co, {"headers": headers})

    def iter_transmute(self, headers: Dict[str, bytes], data: bytes) -> Iterator[bytes]:
        """
        Transmute message body and apply all the transformations
        :param headers:
        :param data:
        :return:
        """

        def spool():
            yield data

        if not self.transmutations:
            yield data
            return

        g = spool()
        for t in self.transmutations:
            g = t.iter_transmute(headers, g)
        yield from g

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
        # Compile match section
        match_eq: DefaultDict[str, List[bytes]] = defaultdict(list)
        match_re: DefaultDict[str, List[bytes]] = defaultdict(list)
        match_ne: List[Tuple[str, bytes]] = []
        for match in route.match:
            if match.is_eq:
                match_eq[match.header] += [smart_bytes(match.value)]
            elif match.is_ne:
                match_ne += [(match.header, smart_bytes(match.value))]
            elif match.is_re:
                match_re[match.header] += [smart_bytes(match.value)]
        expr = []
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
        r.transmutations = [Transmutation.from_transmute(t) for t in route.transmute]
        # Compile action part
        r.actions = [Action.from_action(a) for a in route.action]
        return r
