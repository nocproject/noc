#!./bin/python
# ----------------------------------------------------------------------
# Metrics service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from collections import defaultdict
from typing import Any, Dict, Tuple, Optional
import sys
import asyncio
import codecs
import hashlib

# Third-party modules
import orjson

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.liftbridge.message import Message
from noc.core.perf import metrics
from noc.core.mongo.connection_async import connect_async
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from noc.core.cdag.node.base import BaseCDAGNode
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.scope import MetricScopeCDAGFactory
from noc.services.metrics.changelog import ChangeLog

MetricKey = Tuple[str, Tuple[Tuple[str, Any], ...], Tuple[str, ...]]


@dataclass
class ScopeInfo(object):
    scope: str
    key_fields: Tuple[str]
    key_labels: Tuple[str]
    units: Dict[str, str]


@dataclass
class Card(object):
    __slots__ = ("probes", "senders")
    probes: Dict[str, BaseCDAGNode]
    senders: Tuple[BaseCDAGNode]


class MetricsService(FastAPIService):
    name = "metrics"
    use_mongo = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scopes: Dict[str, ScopeInfo] = {}
        self.scope_cdag: Dict[str, CDAG] = {}
        self.cards: Dict[MetricKey, Card] = {}
        self.graph: Optional[CDAG] = None
        self.change_log: Optional[ChangeLog] = None
        self.start_state: Dict[str, Dict[str, Any]] = {}

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        self.change_log = ChangeLog(self.slot_number)
        connect_async()
        self.load_scopes()
        await self.change_log.compact()  # @todo: Configurable
        self.start_state = await self.change_log.get_state()
        self.graph = CDAG("metrics")
        asyncio.create_task(self.log_runner())
        asyncio.create_task(self.compact_runnner())
        await self.subscribe_stream("metrics", self.slot_number, self.on_metrics)

    async def on_deactivate(self):
        if self.change_log:
            await self.change_log.flush()
            self.change_log = None

    async def log_runner(self):
        self.logger.info("Run log runner")
        while True:
            await asyncio.sleep(1.0)  # @todo: Configurable
            if self.change_log:
                await self.change_log.flush()

    async def compact_runnner(self):
        self.logger.info("Run compact runner")
        while True:
            await asyncio.sleep(300.0)  # @todo: Configurable
            await self.change_log.compact()

    async def on_metrics(self, msg: Message) -> None:
        data = orjson.loads(msg.value)
        state = {}
        for item in data:
            scope = item.get("scope")
            if not scope:
                self.logger.debug("Discard metric without scope: %s", item)
                metrics["discard", ("reason", "without_scope")] += 1
                return  # Discard metric without scope
            si = self.scopes.get(scope)
            if not si:
                self.logger.debug("Unknown scope: %s", item)
                metrics["discard", ("reason", "unknown_scope")] += 1
                return  # Unknown scope
            labels = item.get("labels")
            if si.key_labels and not labels:
                self.logger.debug("No labels: %s", item)
                metrics["discard", ("reason", "no_labels")] += 1
                return  # No labels
            mk = self.get_key(si, item)
            if si.key_fields and not mk[1]:
                self.logger.debug("No key fields: %s", item)
                metrics["discard", ("reason", "no_keyfields")] += 1
                return  # No key fields
            if si.key_labels and len(mk[2]) != len(si.key_labels):
                self.logger.debug("Missed key label: %s", item)
                metrics["discard", ("reason", "missed_keylabel")] += 1
                return  # Missed key label
            card = self.get_card(mk)
            if not card:
                self.logger.info("Cannot instantiate card: %s", item)
                return  # Cannot instantiate card
            state.update(self.activate_card(card, si, item))
        # Save state change
        if state:
            await self.change_log.feed(state)

    def load_scopes(self):
        """
        Load ScopeInfo structures
        :return:
        """
        units = defaultdict(dict)
        for mt in MetricType.objects.all():
            if mt.units:
                units[mt.scope.id][mt.field_name] = mt.units.code
        for ms in MetricScope.objects.all():
            self.logger.debug("Loading scope %s", ms.table_name)
            si = ScopeInfo(
                scope=ms.table_name,
                key_fields=tuple(sorted(kf.field_name for kf in ms.key_fields)),
                key_labels=tuple(sorted(kl.label[:-1] for kl in ms.labels if kl.is_required)),
                units=units[ms.id],
            )
            self.scopes[ms.table_name] = si
            self.logger.debug(
                "[%s] key fields: %s, key labels: %s", si.scope, si.key_fields, si.key_labels
            )

    @staticmethod
    def get_key(si: ScopeInfo, data: Dict[str, Any]) -> MetricKey:
        def iter_key_labels():
            labels = data.get("labels")
            if not labels or not si.key_labels:
                return
            scopes = {f'{ll.rsplit("::", 1)[0]}::': ll for ll in labels}
            for k in si.key_labels:
                v = scopes.get(k)
                if v is not None:
                    yield v

        return (
            si.scope,
            tuple((k, data[k]) for k in si.key_fields if k in data),
            tuple(iter_key_labels()),
        )

    @staticmethod
    def get_key_hash(k: MetricKey) -> str:
        """
        Calculate persistent hash for metric key
        """
        d = hashlib.sha512(str(k).encode("utf-8")).digest()
        return codecs.encode(d, "base-64")[:7].decode("utf-8")

    def get_card(self, k: MetricKey) -> Optional[Card]:
        """
        Generate part of computation graph and collect its viable inputs
        :param k: (scope, ((key field, key value), ...), (key label, ...))
        :return:
        """
        card = self.cards.get(k)
        if card:
            return card
        # Generate new CDAG
        cdag = self.get_scope_cdag(k)
        if not cdag:
            return None
        # Apply CDAG to a common graph and collect inputs to the card
        card = self.project_cdag(cdag, prefix=self.get_key_hash(k))
        self.cards[k] = card
        return card

    def get_scope_cdag(self, k: MetricKey) -> Optional[CDAG]:
        """
        Generate CDAG for a given metric key
        :param k:
        :return:
        """
        # @todo: Still naive implementation based around the scope
        # @todo: Must be replaced by profile/based card stack generator
        scope = k[0]
        if scope in self.scope_cdag:
            return self.scope_cdag[scope]
        # Not found, create new CDAG
        ms = MetricScope.objects.filter(table_name=k[0]).first()
        if not ms:
            return None  # Not found
        cdag = CDAG(f"scope::{k[0]}", {})
        factory = MetricScopeCDAGFactory(cdag, scope=ms, sticky=True)
        factory.construct()
        self.scope_cdag[k[0]] = cdag
        return cdag

    def project_cdag(self, src: CDAG, prefix: str) -> Card:
        """
        Project `src` to a current graph and return the controlling Card
        :param src:
        :return:
        """

        def unscope(x):
            return sys.intern(x.rsplit("::", 1)[-1])

        nodes: Dict[str, BaseCDAGNode] = {}
        # Clone nodes
        for node_id, node in src.nodes.items():
            new_id = f"{prefix}::{node_id}"
            state = self.start_state.pop(new_id, None)
            nodes[node_id] = node.clone(node_id, prefix=prefix, state=state)
        # Subscribe
        for node_id, o_node in src.nodes.items():
            node = nodes[node_id]
            for rs in o_node.iter_subscribers():
                node.subscribe(
                    nodes[rs.node.node_id], rs.input, dynamic=rs.node.is_dynamic_input(rs.input)
                )
        # Compact the strorage
        for node in nodes.values():
            node.freeze()
        # Return resulting cards
        return Card(
            probes={unscope(node.node_id): node for node in nodes.values() if node.name == "probe"},
            senders=tuple(node for node in nodes.values() if node.name == "metrics"),
        )

    def activate_card(
        self, card: Card, si: ScopeInfo, data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Activate card and return changed state
        """
        units = data.get("_units") or {}
        tx = self.graph.begin()
        ts = data["ts"]
        for n in data:
            mu = units.get(n) or si.units.get(n)
            if not mu:
                continue  # Missed field
            probe = card.probes.get(n)
            if not probe:
                continue
            probe.activate(tx, "ts", ts)
            probe.activate(tx, "x", data[n])
            probe.activate(tx, "unit", mu)
        # Activate senders
        for sender in card.senders:
            for kf in si.key_fields:
                kv = data.get(kf)
                if kv is not None:
                    sender.activate(tx, kf, kv)
            sender.activate(tx, "ts", ts)
            sender.activate(tx, "labels", data.get("labels") or [])
        return tx.get_changed_state()


if __name__ == "__main__":
    MetricsService().start()
