# ----------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import operator
from time import time_ns
from collections import defaultdict
from typing import List, DefaultDict, Iterator, Dict, Iterable, Optional, Any
from functools import partial

# Third-party modules
import orjson

# NOC modules
from noc.core.mx import MX_MESSAGE_TYPE, MX_SHARDING_KEY, Message
from noc.core.service.loader import get_service
from noc.core.comp import DEFAULT_ENCODING
from noc.core.perf import metrics
from noc.core.ioloop.util import run_sync
from noc.core.liftbridge.base import STREAM_CONFIG
from .route import Route, DefaultNotificationRoute
from .action import DROP, DUMP

logger = logging.getLogger(__name__)


class Router(object):
    def __init__(self):
        self.chains: DefaultDict[bytes, List[Route]] = defaultdict(list)
        self.routes: Dict[str, Route] = {}
        self.default_route: Optional[DefaultNotificationRoute] = DefaultNotificationRoute()
        self.stream_partitions: Dict[str, int] = {}
        self.svc = get_service()
        # self.out_queue: Optional[QBuffer] = None

    def load(self):
        """
        Load up all the rules and populate the chains
        :return:
        """
        from noc.main.models.messageroute import MessageRoute

        num = 0
        for num, route in enumerate(
            MessageRoute.objects.filter(is_active=True).order_by("order"), start=1
        ):
            self.chains[route.type.encode(encoding=DEFAULT_ENCODING)] += [
                Route.from_data(route.get_route_config())
            ]
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
            self.rebuild_chains([r_type], deleted=True)

    def rebuild_chains(self, r_types: Optional[Iterable[str]] = None, deleted: bool = False):
        """
        Rebuild Router Chains
        Need lock ?
        :param r_types: List types for rebuild chains
        :param deleted: Route was deleted
        :return:
        """
        chains = defaultdict(list)
        for r in self.routes.values():
            if r_types and r.type not in r_types:
                continue
            chains[r.type].append(r)
        if deleted:
            # Remove last route
            for rt in set(r_types) - set(chains):
                chains[rt] = []
        for chain in chains:
            logger.info("[%s] Rebuild chain", chain)
            self.chains[chain.encode(encoding=DEFAULT_ENCODING)] = list(
                sorted(
                    [r for r in chains[chain]],
                    key=operator.attrgetter("order"),
                )
            )

    def iter_route(self, msg: Message) -> Iterator[Route]:
        mt = msg.headers.get(MX_MESSAGE_TYPE)
        if not mt:
            return
        # Check default Route
        if self.default_route and self.default_route.is_match(msg):
            yield self.default_route
        # Iterate over routes
        for route in self.chains[mt]:
            if route.is_match(msg):
                yield route

    async def publish(
        self,
        value: bytes,
        stream: str,
        partition: Optional[int] = None,
        key: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ):
        # if self.out_queue:
        #    self.out_queue.put(stream, partition, data=value)
        # else:
        self.svc.publish(value=value, stream=stream, partition=partition, headers=headers)

    def route_sync(self, msg: Message):
        """
        Synchronize method
        :param msg:
        :return:
        """
        run_sync(partial(self.route_message, msg))

    @staticmethod
    def get_message(
        data: Any,
        message_type: str,
        headers: Optional[Dict[str, bytes]] = None,
        sharding_key: int = 0,
    ) -> Message:
        """
        Build message

        :param data: Data for transmit
        :param message_type: Message type
        :param headers: additional message headers
        :param sharding_key: Key for sharding
        :return:
        """
        msg_headers = {
            MX_MESSAGE_TYPE: message_type.encode(DEFAULT_ENCODING),
            MX_SHARDING_KEY: str(sharding_key).encode(DEFAULT_ENCODING),
        }
        if headers:
            msg_headers.update(headers)
        if not isinstance(data, bytes):
            data = orjson.dumps(data)
        return Message(
            value=data,
            headers=msg_headers,
            timestamp=time_ns(),
            key=sharding_key,
        )

    async def route_message(self, msg: Message, msg_id: Optional[str] = None):
        """
        Route message by rule
        :param msg:
        :param msg_id:
        :return:
        """
        # Apply routes
        for route in self.iter_route(msg):
            metrics["route_hits", ("type", route.type)] += 1
            logger.debug("[%d] Applying route %s", msg_id, route.name)
            # Apply actions
            routed: bool = False
            for stream, action_headers, body in route.iter_action(msg):
                metrics["action_hits", ("stream", stream)] += 1
                # Fameless drop
                if stream == DROP:
                    metrics["action_drops", ("stream", stream)] += 1
                    logger.debug("[%s] Dropped. Stopping processing", msg_id)
                    return
                elif stream == DUMP:
                    logger.info(
                        "[%s] Dump. Message headers: %s;\n-----\n Body: %s \n----\n ",
                        msg_id,
                        msg.headers,
                        msg.value,
                    )
                    continue
                # Build resulting headers
                headers = {}
                headers.update(msg.headers)
                if action_headers:
                    headers.update(action_headers)
                # Determine sharding channel
                sharding_key = int(headers.get(MX_SHARDING_KEY, b"0"))
                partitions = self.stream_partitions.get(stream)
                if not partitions:
                    # Request amount of partitions
                    sc = STREAM_CONFIG[stream]
                    partitions = sc.get_partitions()
                    self.stream_partitions[stream] = partitions
                partition = sharding_key % partitions
                # Single message may be transmuted in zero or more messages
                body = route.transmute(headers, body)
                # for body in route.iter_transmute(headers, msg.value):
                if not isinstance(body, bytes):
                    # Transmute converts message to an arbitrary structure,
                    # so convert back to the json
                    body = orjson.dumps(body)
                metrics[("forwards", ("stream", stream))] += 1
                logger.debug("[%s] Routing to %s:%s", msg_id, stream, partition)
                await self.publish(value=body, stream=stream, partition=partition, headers=headers)
                routed = True
            if not routed:
                logger.debug("[%d] Not routed", msg_id)
                metrics[
                    "route_misses",
                    ("message_type", msg.headers.get(MX_MESSAGE_TYPE).decode(DEFAULT_ENCODING)),
                ] += 1
        # logger.debug("[%s] Finish processing", msg_id)
