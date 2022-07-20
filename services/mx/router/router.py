# ----------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import operator
from collections import defaultdict
from typing import List, DefaultDict, Iterator, Dict, Iterable, Optional

# NOC modules
from noc.core.liftbridge.message import Message
from noc.core.mx import MX_MESSAGE_TYPE
from noc.main.models.messageroute import MessageRoute
from noc.core.comp import smart_bytes
from .route import Route

logger = logging.getLogger(__name__)


class Router(object):
    def __init__(self):
        self.chains: DefaultDict[bytes, List[Route]] = defaultdict(list)
        self.routes: Dict[str, Route] = {}

    def load(self):
        """
        Load up all the rules and populate the chains
        :return:
        """
        num = 0
        for num, route in enumerate(
            MessageRoute.objects.filter(is_active=True).order_by("order"), start=1
        ):
            self.chains[smart_bytes(route.type)] += [Route.from_route(route)]
        logger.info("Loading %s route", num)

    def has_route(self, route_id: str) -> bool:
        """
        Check Route already exists in chains
        :param route_id:
        :return:
        """
        return route_id in self.routes

    def change_route(self, data):
        """
        Update route in chain
        If change Chain -
        * change type = delete + insert
        * change order = reorder
        * change data = update
        :param data:
        :return:
        """
        r = Route.from_data(data)
        route_id = data["id"]
        to_rebuild = set()
        if not self.has_route(route_id):
            self.routes[data["id"]] = r
            to_rebuild.add(r.type)
            logger.info("[%s|%s] Insert route", route_id, data["name"])
            self.rebuild_chains(to_rebuild)
            return
        if self.routes[route_id].type != r.type:
            # rebuild
            logger.info(
                "[%s|%s] Change route chain: %s -> %s",
                route_id,
                data["name"],
                self.routes[route_id].type,
                r.type,
            )
            to_rebuild.add([r.type, self.routes[route_id].type])
            self.routes[route_id].set_type(r.type)
        if self.routes[route_id].order != r.order:
            logger.info(
                "[%s|%s] Change route order: %s -> %s",
                route_id,
                data["name"],
                self.routes[route_id].order,
                r.order,
            )
            self.routes[route_id].set_order(r.order)
            to_rebuild.add(r.type)
        if self.routes[route_id].is_differ(data):
            logger.info("[%s|%s] Update route", route_id, data["name"])
            self.routes[route_id].update(data)
        if to_rebuild:
            self.rebuild_chains(to_rebuild)

    def delete_route(self, route_id: str):
        """
        Delete Route from Chains
        :param route_id:
        :return:
        """
        r_type = None
        if route_id in self.routes:
            logger.info("[%s|%s] Delete route", route_id, self.routes[route_id].name)
            r_type = self.routes[route_id].type
            del self.routes[route_id]
        if r_type:
            self.rebuild_chains([r_type])

    def rebuild_chains(self, r_types: Optional[Iterable[str]] = None):
        """
        Rebuild Router Chains
        Need lock ?
        :param r_types: List types for rebuild chains
        :return:
        """
        chains = defaultdict(list)
        for r in self.routes.values():
            if r_types and r.type not in r_types:
                continue
            chains[r.type].append(r)
        for chain in chains:
            logger.info("[%s] Rebuild chain", chain)
            self.chains[smart_bytes(chain)] = list(
                sorted(
                    [r for r in chains[chain]],
                    key=operator.attrgetter("order"),
                )
            )

    def iter_route(self, msg: Message) -> Iterator[Route]:
        mt = msg.headers.get(MX_MESSAGE_TYPE)
        if not mt:
            return
        for route in self.chains[mt]:
            if route.is_match(msg):
                yield route
