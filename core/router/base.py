# ----------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import operator
import itertools
from time import time_ns
from collections import defaultdict
from typing import List, DefaultDict, Iterator, Dict, Iterable, Optional, Any
from functools import partial

# Third-party modules
import orjson

# NOC modules
from noc.core.mx import MX_MESSAGE_TYPE, MX_SHARDING_KEY, Message, MX_SPAN_ID, MX_SPAN_CTX
from noc.core.service.loader import get_service
from noc.core.comp import DEFAULT_ENCODING
from noc.core.perf import metrics
from noc.core.ioloop.util import run_sync
from noc.core.msgstream.config import get_stream
from noc.core.span import Span
from .route import Route, DefaultNotificationRoute
from .action import DROP, DUMP

logger = logging.getLogger(__name__)


class Router(object):
    DEFAULT_CHAIN = "default"

    def __init__(self):
        self.chains: DefaultDict[bytes, List[Route]] = defaultdict(list)
        self.routes: Dict[str, Route] = {
            self.DEFAULT_CHAIN: DefaultNotificationRoute(),  # Add default route for notification
        }
        self.stream_partitions: Dict[str, int] = {}
        self.svc = get_service()
        # Add default
        self.rebuild_chains([b"*"])
        # self.out_queue: Optional[QBuffer] = None

    def load(self):
        """Load up all the rules and populate the chains"""
        from noc.main.models.messageroute import MessageRoute

        num = 0
        for num, route in enumerate(
            MessageRoute.objects.filter(is_active=True).order_by("order"), start=1
        ):
            cfg = route.get_route_config()
            cfg["type"] = cfg["type"].value
            self.chains[route.type] += [Route.from_data(cfg)]
        logger.info("Loading %s route", num)
        self.rebuild_chains()

    def has_route(self, route_id: str) -> bool:
        """
        Check Route already exists in chains
            route_id: Router identifier
        """
        return route_id in self.routes

    def change_route(self, data):
        """
        Update route in chain
        If change Chain -
        * change type = delete + insert
        * change order = reorder
        * change data = update
        Attrs:
            data:
        """
        r = Route.from_data(data)
        route_id = data["id"]
        to_rebuild = set()
        if not self.has_route(route_id):
            self.routes[data["id"]] = r
            to_rebuild |= r.m_types
            logger.info("[%s|%s] Insert route", route_id, data["name"])
            self.rebuild_chains(to_rebuild)
            return
        if self.routes[route_id].m_types != r.m_types:
            # rebuild
            logger.info(
                "[%s|%s] Change route chain: %s -> %s",
                route_id,
                data["name"],
                b";".join(sorted(self.routes[route_id].m_types)),
                b";".join(sorted(r.m_types)),
            )
            to_rebuild |= r.m_types.symmetric_difference(self.routes[route_id].m_types)
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
            to_rebuild |= r.m_types
        if self.routes[route_id].is_differ(data):
            logger.info("[%s|%s] Update route", route_id, data["name"])
            self.routes[route_id].update(data)
        if to_rebuild:
            self.rebuild_chains(to_rebuild)

    def delete_route(self, route_id: str):
        """
        Delete Route from Chains
        Attrs:
            route_id: Router Identifiers
        """
        r_type = None
        if route_id in self.routes:
            logger.info("[%s|%s] Delete route", route_id, self.routes[route_id].name)
            r_type = self.routes[route_id].m_types
            del self.routes[route_id]
        if r_type:
            self.rebuild_chains(r_type, deleted=True)

    def rebuild_chains(self, r_types: Optional[Iterable[bytes]] = None, deleted: bool = False):
        """
        Rebuild Router Chains
        Need lock ?
        Attrs:
            r_types: List types for rebuild chains
            deleted: Route was deleted flag
        """
        chains = defaultdict(list)
        r_types = frozenset(r_types) if r_types else None
        for rid, r in self.routes.items():
            if r_types and not r.m_types.intersection(r_types) and rid != self.DEFAULT_CHAIN:
                continue
            elif r_types:
                updated_types = r.m_types.intersection(r_types)
            else:
                updated_types = r.m_types
            for tt in updated_types:
                chains[tt].append(r)
        if deleted:
            # Remove last route
            for rt in set(r_types) - set(chains):
                chains[rt] = []
        for chain in chains:
            logger.info("[%s] Rebuild chain", chain)
            self.chains[chain] = list(
                sorted(
                    [r for r in chains[chain]],
                    key=operator.attrgetter("order"),
                )
            )

    def iter_route(self, msg: Message, message_type: bytes) -> Iterator[Route]:
        # Iterate over routes
        for route in itertools.chain(self.chains[message_type], self.chains[b"*"]):
            if route.is_match(msg, message_type):
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
            msg: Route Message
        """
        run_sync(partial(self.route_message, msg))

    @staticmethod
    def get_message(
        data: Any,
        message_type: str,
        headers: Optional[Dict[str, bytes]] = None,
        sharding_key: int = 0,
        raw_value: bool = False,
    ) -> Message:
        """
        Build message
        Attrs:
            data: Data for transmit
            message_type: Message type
            headers: additional message headers
            sharding_key: Key for sharding
            raw_value:
        """
        msg_headers = {
            MX_MESSAGE_TYPE: message_type.encode(DEFAULT_ENCODING),
            MX_SHARDING_KEY: str(sharding_key).encode(DEFAULT_ENCODING),
        }
        if headers:
            msg_headers.update(headers)
        if not raw_value and not isinstance(data, bytes):
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
        Attrs:
            msg: Received Message
            msg_id: Message sequence number
        """
        mt = msg.headers.get(MX_MESSAGE_TYPE)
        if not mt:
            return
        # Apply routes
        for route in self.iter_route(msg, mt):
            metrics["route_hits", ("type", route.type)] += 1
            logger.debug("[%s] Applying route %s", msg_id, route.name)
            # Apply actions
            routed: bool = False
            with Span(
                sample=int(route.telemetry_sample),
                server=self.svc.name,
                service=route.name,
                in_label=msg.key,
            ) as span:
                for stream, action_headers, body in route.iter_action(msg, mt):
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
                    if partitions is None:
                        # Request amount of partitions
                        try:
                            sc = get_stream(stream)
                            partitions = sc.get_partitions()
                        except ValueError:
                            partitions = 1
                        self.stream_partitions[stream] = partitions
                    if not partitions:
                        logger.info("[%s] No partition for stream: %s. Skipping...", msg, stream)
                        continue
                    partition = sharding_key % partitions
                    # Single message may be transmuted in zero or more messages
                    try:
                        body = route.transmute(headers, body)
                    except Exception as e:
                        logger.error(
                            "[%s] Error when transmute message %s: %s",
                            msg.timestamp,
                            body[:500],
                            str(e),
                        )
                        continue
                    if body is None:
                        logger.debug("[%s] Skip empty message", msg.timestamp)
                        continue
                    # for body in route.iter_transmute(headers, msg.value):
                    if not isinstance(body, bytes):
                        # Transmute converts message to an arbitrary structure,
                        # so convert back to the json
                        body = orjson.dumps(body)
                    metrics[("forwards", ("stream", stream))] += 1
                    logger.debug("[%s] Routing to %s:%s", msg_id, stream, partition)
                    if route.telemetry_sample:
                        headers[MX_SPAN_ID] = str(span.span_id).encode(DEFAULT_ENCODING)
                        headers[MX_SPAN_CTX] = str(span.span_context).encode(DEFAULT_ENCODING)
                        span.headers = headers
                    await self.publish(
                        value=body, stream=stream, partition=partition, headers=headers
                    )
                    routed = True
                if not routed:
                    logger.debug("[%s] Not routed", msg_id)
                    metrics[
                        "route_misses",
                        ("message_type", msg.headers.get(MX_MESSAGE_TYPE).decode(DEFAULT_ENCODING)),
                    ] += 1
        # logger.debug("[%s] Finish processing", msg_id)
