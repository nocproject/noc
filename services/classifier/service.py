#!./bin/python
# ---------------------------------------------------------------------
# Classifier service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import os
import enum
import operator
import re
import socket
import struct
import asyncio
from time import perf_counter
from typing import Optional, Dict, List, Callable, Tuple, Any

# Third-party modules
import cachetools
import orjson
import bson


# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService
from noc.core.perf import metrics
from noc.core.error import NOCError
from noc.core.version import version
from noc.core.debug import error_report
from noc.core.escape import fm_unescape
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.comp import DEFAULT_ENCODING
from noc.core.msgstream.message import Message
from noc.core.wf.diagnostic import SNMPTRAP_DIAG, SYSLOG_DIAG, DiagnosticState
from noc.core.fm.event import Event, EventSource, Target, Var, EventSeverity
from noc.core.mx import MessageType
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.pool import Pool
from noc.fm.models.eventclass import EventClass
from noc.fm.models.mib import MIB
from noc.fm.models.mibdata import MIBData
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import GENERIC_PROFILE
from noc.services.classifier.ruleset import RuleSet
from noc.services.classifier.patternset import PatternSet
from noc.services.classifier.evfilter.dedup import DedupFilter
from noc.services.classifier.evfilter.suppress import SuppressFilter
from noc.services.classifier.abdetector import AbductDetector
from noc.services.classifier.datastream import (
    EventRuleDataStreamClient,
    EventConfigDataStreamClient,
)
from noc.services.classifier.actionset import ActionSet, EventAction
from noc.services.classifier.eventconfig import EventConfig


class EventMetrics(enum.Enum):
    CR_FAILED = "events_failed"
    CR_DELETED = "events_deleted"
    CR_IGNORED = "events_ignored"
    CR_SUPPRESSED = "events_suppressed"
    CR_UNKNOWN = "events_unknown"
    CR_CLASSIFIED = "events_classified"
    CR_DISPOSED = "events_disposed"
    CR_DUPLICATED = "events_duplicated"
    CR_UDUPLICATED = "events_unk_duplicated"
    CR_UOBJECT = "events_unk_object"
    CR_PROCESSED = "events_processed"
    CR_PREPROCESSED = "events_preprocessed"


E_SRC_MX_MESSAGE = {
    EventSource.SYSLOG: "syslog",
    EventSource.SNMP_TRAP: "snmptrap",
    EventSource.SYSTEM: "system",
    EventSource.OTHER: "other",
}

E_SRC_METRICS = {
    EventSource.SYSLOG: "events_syslog",
    EventSource.SNMP_TRAP: "events_snmp_trap",
    EventSource.SYSTEM: "events_system",
    EventSource.OTHER: "events_other",
}

NS = 1_000_000_000.0

CABLE_ABDUCT = "Security | Abduct | Cable Abduct"

SNMP_TRAP_OID = "1.3.6.1.6.3.1.1.4.1.0"


class ClassifierService(FastAPIService):
    """
    Events-classification service
    """

    name = "classifier"
    pooled = True
    use_mongo = True
    use_router = True
    process_name = "noc-%(name).10s-%(pool).5s"

    # SNMP OID pattern
    rx_oid = re.compile(r"^(\d+\.){6,}")

    _interface_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

    def __init__(self):
        super().__init__()
        self.version: str = version.version
        self.ruleset: RuleSet = RuleSet()
        self.pattern_set: PatternSet = PatternSet()
        self.action_set: ActionSet = ActionSet(logger=self.logger)
        self.event_config: Dict[str, EventConfig] = {}
        self.default_event_config: EventConfig = None
        self.alter_handlers: List[Tuple[str, bool, Callable]] = []
        self.unclassified_codebook_depth = 5
        self.unclassified_codebook: Dict[str, List[str]] = {}  # object id -> [<codebook>]
        self.handlers: Dict[str, List[Callable]] = {}  # event class id -> [<handler>]
        self.dedup_filter: DedupFilter = DedupFilter()
        self.suppress_filter: SuppressFilter = SuppressFilter()
        self.abduct_detector: AbductDetector = AbductDetector()
        # Default link event action, when interface is not in inventory
        self.default_link_action = None
        # Sync primitives
        self.event_rules_ready_event = asyncio.Event()
        self.event_config_ready = asyncio.Event()
        # Reporting
        self.last_ts: Optional[float] = None
        self.stats: Dict[EventMetrics, int] = {}
        #
        self.slot_number = 0
        self.total_slots = 0
        self.add_configs = 0
        self.pool_partitions: Dict[str, int] = {}
        #
        self.cable_abduct_ecls: Optional[EventClass] = None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_interface_cache"))
    def get_interface(
        cls, managed_object_id, name, ifindex: Optional[int] = None
    ) -> Optional[Tuple[str, Any]]:
        """
        Get interface instance
        """
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        q = {"managed_object": managed_object_id}
        if name:
            q["name"] = name
        elif ifindex:
            q["ifindex"] = int(ifindex)
        else:
            return
        iface = Interface.objects.filter(**q).scalar("name", "profile").first()
        if iface:
            return iface
        si = SubInterface.objects.filter(**q).scalar("name", "profile").first()
        if si:
            return si

    async def on_activate(self):
        """
        Load rules from database after loading config
        """
        self.logger.info("Using rule lookup solution: %s", config.classifier.lookup_handler)
        self.ruleset.load(skip_load_rules=config.datastream.enable_cfgeventrules)
        self.pattern_set.load()
        self.load_link_action()
        # Heat up MIB cache
        MIBData.preload()
        self.slot_number, self.total_slots = await self.acquire_slot()
        # Start tracking changes
        if config.datastream.enable_cfgevent:
            asyncio.get_running_loop().create_task(self.get_event_config_mappings())
            await self.event_config_ready.wait()
            self.logger.info("Handlers are loaded: %s", self.action_set.add_handlers)
        else:
            await self.load_event_configs()
            self.action_set.load()
        if config.datastream.enable_cfgeventrules:
            asyncio.get_running_loop().create_task(self.get_event_rules_mappings())
            await self.event_rules_ready_event.wait()
        report_callback = PeriodicCallback(self.report, 1000)
        report_callback.start()
        await self.subscribe_stream(
            "events.%s" % config.pool,
            self.slot_number,
            self.on_event,
            async_cursor=config.classifier.allowed_async_cursor,
        )

    async def get_event_rules_mappings(self):
        """Subscribe and track datastream changes"""
        # Register RPC aliases
        client = EventRuleDataStreamClient("cfgeventrules", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track event classification rules")
            try:
                await client.query(
                    limit=config.classifier.ds_limit,
                    block=True,
                    filter_policy="delete",
                )
            except NOCError as e:
                self.logger.info("Failed to get Event Classification Rules: %s", e)
                await asyncio.sleep(1)

    async def get_event_config_mappings(self):
        """Subscribe and track datastream changes"""
        # Register RPC aliases
        client = EventConfigDataStreamClient("cfgevent", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track event configs")
            try:
                await client.query(
                    limit=config.classifier.ds_limit,
                    block=True,
                    filter_policy="delete",
                )
            except NOCError as e:
                self.logger.info("Failed to get Event Configs: %s", e)
                await asyncio.sleep(1)

    def load_link_action(self):
        self.default_link_action = None
        if config.classifier.default_interface_profile:
            p = InterfaceProfile.objects.filter(
                name=config.classifier.default_interface_profile
            ).first()
            if p:
                self.logger.info("Setting default link event action to %s", p.link_events)
                self.default_link_action = p.link_events

    async def load_event_configs(self):
        for ec in EventClass.objects.filter():
            await self.update_config(EventClass.get_event_config(ec))
        self.logger.info("Loading configs: %s", self.add_configs)

    async def register_mx_message(
        self,
        event: "Event",
        event_config: EventConfig,
        resolved_vars: Dict[str, Any],
        mo: Optional[ManagedObject],
    ):
        """
        Send event message to MX service
        Args:
            event:
            event_config: Resolved Event Class
            resolved_vars: Raw variables for 'SNMP Trap' event
            mo: Managed Object instance
        """
        metrics["events_message"] += 1
        self.logger.debug(
            "[%s|%s|%s] Register MX message",
            event.id,
            event.target.name,
            event.target.address,
        )
        msg = {
            "timestamp": event.timestamp,
            "message_id": resolved_vars.get("message_id"),
            "collector_type": E_SRC_MX_MESSAGE[event.type.source],
            "collector": event.target.pool,
            "address": event.target.address,
            "managed_object": mo.get_message_context() if mo else None,
            "event_class": {"id": str(event_config.event_class_id), "name": event_config.name},
            "event_vars": event.vars,
        }
        if event.type.source == EventSource.SYSLOG:
            msg["data"] = {
                "facility": event.type.facility or "",
                "severity": event.type.severity or "",
                "message": event.message or "",
            }
        elif event.type.source == EventSource.SNMP_TRAP:
            msg["data"] = {"vars": resolved_vars.pop("raw")}
        else:
            msg["data"] = {d.name: d.value for d in event.data}
        # Register MX message
        await self.send_message(
            message_type=MessageType.EVENT,
            data=orjson.dumps(msg),
            sharding_key=int(mo.id),
            headers=mo.get_mx_message_headers(),
        )

    def register_log(
        self,
        event: Event,
        event_config: EventConfig,
        message: str,
        managed_object: Optional[ManagedObject] = None,
    ):
        """
        Register Event log
        Args:
            event: Event instance
            event_config: Event Config
            message: message sting
            managed_object: ManagedObject instance
        """
        data = {
            "date": event.timestamp.date(),
            "ts": event.timestamp.isoformat(),
            "event_id": str(event.id or ""),
            "op": "new",
            "managed_object": managed_object.bi_id if managed_object else 0,
            "target": event.target.model_dump(exclude={"is_agent"}, exclude_none=True),
            "target_reference": event.target.reference,
            "event_class": event_config.bi_id,
            "message": message,
        }
        self.register_metrics("disposelog", [data])

    def get_event_config(self, event_class: str) -> EventConfig:
        """Getting EventConfig"""
        if str(event_class) not in self.event_config:
            return self.default_event_config
        return self.event_config[str(event_class)]

    async def classify_event(
        self,
        event: Event,
        raw_vars: Dict[str, Any],
    ) -> Tuple[EventAction, Optional["EventConfig"], Optional[Dict[str, Any]]]:
        """
        Perform event classification.
        Classification steps are:

        1. Format SNMP values according to MIB definitions (for SNMP events only)
        2. Find matching classification rule
        3. Calculate rule variables

        Args:
            event: Event to classify
            raw_vars: Resolved vars
            mo: Target ManagedObject
        :returns: Classification status (CR_*)
        """
        metrics[E_SRC_METRICS.get(event.type.source)] += 1
        # Get matched event class
        if event.type.event_class:
            event_class = EventClass.get_by_name(event.type.event_class)
            if not event_class:
                self.logger.error(
                    "[%s|%s|%s] Failed to process event: Invalid event class '%s'",
                    event.id,
                    event.target.name,
                    event.target.address,
                    event.type.event_class,
                )
                metrics[EventMetrics.CR_FAILED] += 1
                return EventAction.DROP, None, None  # Drop malformed message
            metrics[EventMetrics.CR_PREPROCESSED] += 1
            if not event.vars:
                return EventAction.LOG, self.get_event_config(event_class.id), raw_vars
            return EventAction.LOG, self.get_event_config(event_class.id), event.vars
        # Prevent unclassified events flood
        if self.check_unclassified_syslog_flood(event):
            return EventAction.DROP, None, None
        rule, r_vars = self.ruleset.find_rule(event, raw_vars)
        if rule is None:
            # Something goes wrong.
            # No default rule found. Exit immediately
            self.logger.error("No default rule found. Exiting")
            os._exit(1)
        if rule.to_drop:
            # Silently drop event if declared by action
            event.type.severity = EventSeverity.IGNORED
            self.logger.info(
                "[%s|%s|%s] Dropped by action",
                event.id,
                event.target.name,
                event.target.address,
            )
            metrics[EventMetrics.CR_DELETED] += 1
            return EventAction.DROP, self.get_event_config(rule.event_class_id), r_vars
        # Apply transform
        for t in rule.vars_transform or []:
            t.transform(r_vars, raw_vars)
        if rule.is_unknown_syslog:
            # Append to codebook
            cb = self.get_msg_codebook(event.message or "")
            o_id = event.target.id
            if o_id not in self.unclassified_codebook:
                self.unclassified_codebook[o_id] = []
            cbs = [cb] + self.unclassified_codebook[o_id]
            cbs = cbs[: self.unclassified_codebook_depth]
            self.unclassified_codebook[o_id] = cbs
        self.logger.debug(
            "[%s|%s|%s] Matching rule: %s",
            event.id,
            event.target.name,
            event.target.address,
            rule.name,
        )
        # event.event_class = rule.event_class
        # message = f"Classified as '{rule.event_class.name}' by rule '{rule.name}'"
        event_config = self.get_event_config(rule.event_class_id)
        self.register_log(
            event,
            event_config,
            f"Classified as '{rule.event_class_name}' by rule '{rule.name}'",
        )
        if rule.is_unknown:
            metrics[EventMetrics.CR_UNKNOWN] += 1
        else:
            metrics[EventMetrics.CR_CLASSIFIED] += 1
        return EventAction.LOG, event_config, r_vars

    async def dispose_event(self, event: Event, mo: ManagedObject):
        """
        Register Alarm
        Args:
            event: Event instance
            mo: ManagedObject Instance
        """
        self.logger.info(
            "[%s|%s|%s] Disposing",
            event.id,
            event.target.name,
            event.target.address,
        )
        # Calculate partition
        fm_pool = mo.get_effective_fm_pool().name
        stream = f"dispose.{fm_pool}"
        num_partitions = self.pool_partitions.get(fm_pool)
        if not num_partitions:
            num_partitions = await self.get_stream_partitions(stream)
            self.pool_partitions[fm_pool] = num_partitions
        partition = int(mo.id) % num_partitions
        event.target.id = str(mo.id)
        self.publish(
            orjson.dumps({"$op": "event", "event_id": str(event.id), "event": event.model_dump()}),
            # To dispose
            stream=stream,
            partition=partition,
        )
        metrics[EventMetrics.CR_DISPOSED] += 1

    def deduplicate_event(
        self,
        event: Event,
        event_config: EventConfig,
        event_vars: Dict[str, Any],
    ) -> bool:
        """
        Deduplicate event when necessary
        Args:
            event: Event Instance
            event_config: EventConfig Instance
            event_vars:
        Return: True, if event is duplication of existent one
        """
        if "dedup" not in event_config.filters:
            return False
        de_id = self.dedup_filter.find(event, event_config, event_vars)
        if not de_id:
            return False
        self.logger.info(
            "[%s|%s|%s] Duplicates event %s. Discarding",
            event.id,
            event.target.name,
            event.target.address,
            de_id,
        )
        # de.log_message("Duplicated event %s has been discarded" % event.id)
        metrics[EventMetrics.CR_DUPLICATED] += 1
        return True

    def suppress_repeats(self, event: Event, event_config: EventConfig) -> bool:
        """
        Suppress repeated events
        Args:
            event:
            event_config:
        """
        if "suppress" not in event_config.filters:
            return False
        se_id = self.suppress_filter.find(event, event_config)
        if not se_id:
            return False
        self.logger.info(
            "[%s|%s|%s] Suppressed by event %s",
            event.id,
            event.target.name,
            event.target.address,
            se_id,
        )
        # Update suppressing event, event log
        self.register_log(event, event_config, "Event suppression")
        # Delete suppressed event
        metrics[EventMetrics.CR_SUPPRESSED] += 1
        return True

    def check_unclassified_syslog_flood(self, event: Event) -> bool:
        """Check if incoming messages is in unclassified codebook"""
        if event.type.source != EventSource.SYSLOG:
            return False
        pcbs = self.unclassified_codebook.get(event.target.id)
        if not pcbs:
            return False
        cb = self.get_msg_codebook(event.message)
        for pcb in pcbs:
            if self.is_codebook_match(cb, pcb):
                # Signature is already seen, suppress
                metrics[EventMetrics.CR_UDUPLICATED] += 1
                return True
        return False

    def resolve_vars(self, event: Event) -> Dict[str, Any]:
        """
        Resolve Event data list to vars
        Args:
            event:
        """
        # Store event variables, without snmp_raw
        # Detect profile by rule (for SNMP message)
        # Syslog - ignore profile
        raw_vars, snmp_vars = {"profile": event.type.profile, "message": event.message}, {}
        for d in event.data:
            if d.snmp_raw:
                snmp_vars[d.name] = d.value
            else:
                raw_vars[d.name] = fm_unescape(d.value).decode(DEFAULT_ENCODING)
        # Resolve MIB variables for SNMP Traps
        if snmp_vars:
            for k, v in MIB.resolve_vars(
                snmp_vars, include_raw=config.message.enable_event
            ).items():
                v = fm_unescape(v).decode(DEFAULT_ENCODING)
                event.data.append(Var(name=k, value=v))
                raw_vars[k] = v
            # Append resolved vars to data
        return raw_vars

    @classmethod
    def resolve_object(
        cls, target: Target, remote_system: Optional[str] = None
    ) -> Optional[ManagedObject]:
        """
        Resolve Managed Object by target

        Args:
            target: Event Target
            remote_system: Remote System name
        """
        mo = None
        if target.id and not target.is_agent:
            mo = ManagedObject.get_by_id(int(target.id))
        if not mo and target.remote_id and remote_system:
            remote_system = RemoteSystem.get_by_name(remote_system)
            mo = ManagedObject.get_by_mapping(remote_system, target.remote_id)
        if not mo and target.pool:
            mo = ManagedObject.objects.filter(pool=target.pool, address=target.address).first()
        return mo

    async def on_event(self, msg: Message):
        # Process Span (trace)
        # Decode message
        try:
            event = Event(**orjson.loads(msg.value))
        except ValueError as e:
            metrics[EventMetrics.CR_FAILED] += 1
            # Convert Old
            self.logger.error("Unknown message format: %s", e)
            return
        # Generate or reuse existing object id
        try:
            event.id = str(bson.ObjectId(event.id))
        except bson.errors.InvalidId:
            self.logger.warning("Invalid event_id: %s", event.id)
            event.id = str(bson.ObjectId())
        # Calculate message processing delay
        lag = (time.time() - float(msg.timestamp) / NS) * 1000
        metrics["lag_us"] = int(lag * 1000)
        self.logger.debug("[%s] Receiving new event: %s (Lag: %.2fms)", event.id, event.data, lag)
        metrics[EventMetrics.CR_PROCESSED] += 1
        # Ignore event by rules
        if self.pattern_set.find_ignore_rule(event):
            self.logger.debug(
                "[%s|%s|%s] Ignored event %s vars %s",
                event.id,
                event.target.name,
                event.target.address,
                event,
                event.vars,
            )
            metrics[EventMetrics.CR_IGNORED] += 1
            return
        # Resolve managed object
        mo = self.resolve_object(event.target, remote_system=event.remote_system)
        if not mo:
            self.logger.info("[%s] Unknown managed object id %s. Skipping", event.id, event.target)
            event.type.profile = GENERIC_PROFILE
            metrics[EventMetrics.CR_UOBJECT] += 1
        else:
            self.update_diagnostic(mo, event)
            event.type.profile = mo.profile.name
            self.logger.info("[%s|%s|%s] Managed object found", event.id, mo.name, mo.address)
        # Process event
        resolved_vars = self.resolve_vars(event)
        try:
            e_action, e_cfg, resolved_vars = await self.classify_event(event, resolved_vars)
        except Exception as e:
            self.logger.error(
                "[%s|%s|%s] Failed to process event: %s",
                event.id,
                event.target.name,
                event.target.address,
                e,
            )
            metrics[EventMetrics.CR_FAILED] += 1
            error_report()
            return
        if e_action == EventAction.DROP:
            metrics[EventMetrics.CR_DELETED] += 1
            self.logger.info(
                "[%s|%s|%s] Dropped by Rule",
                event.id,
                event.target.name,
                event.target.address,
            )
            return
        event.type.event_class = e_cfg.event_class
        # Deduplication
        if self.deduplicate_event(event, e_cfg, resolved_vars):
            return
        duplicate_vars = resolved_vars.copy()
        # Fill deduplication filter
        self.dedup_filter.register(event, e_cfg, duplicate_vars)
        # Calculate rule variables
        event.vars, e_res, error = self.ruleset.eval_vars(resolved_vars, mo, e_cfg=e_cfg)
        if not error:
            self.logger.info(
                "[%s|%s|%s] Event processed successfully: %s",
                event.id,
                event.target.name,
                event.target.address,
                e_cfg.event_class,
            )
        else:
            e_action = EventAction.LOG_ERROR
            self.logger.info(
                "[%s|%s|%s] Event processed with error: %s/%s",
                event.id,
                event.target.name,
                event.target.address,
                e_cfg.event_class,
                error,
            )
            self.register_event(event, e_cfg, e_action, resolved_vars, mo, error=error)
            return
        # Suppress repeats
        if event.vars and self.suppress_repeats(event, e_cfg):
            return
        # Fill suppress filter
        self.suppress_filter.register(event, e_cfg)
        # Call Actions
        e_action = self.action_set.run_actions(event, mo, e_res, config=e_cfg) or e_action
        self.register_event(event, e_cfg, e_action, resolved_vars, mo)
        if config.message.enable_event:
            await self.register_mx_message(event, e_cfg, resolved_vars, mo)
        if e_action == EventAction.DROP:
            self.logger.info(
                "[%s|%s|%s] Dropped by action",
                event.id,
                event.target.name,
                event.target.address,
            )
            metrics[EventMetrics.CR_DELETED] += 1
            return
        if event.type.severity == EventSeverity.IGNORED:
            # Severity ignored
            return
        # Finally dispose event to further processing by correlator
        if mo and e_action == EventAction.DISPOSITION:
            await self.dispose_event(event, mo)

    async def report(self):
        t = perf_counter()
        if self.last_ts:
            r = []
            for m in EventMetrics:
                ov = self.stats.get(m, 0)
                nv = metrics[m].value
                r += [f"{m.name}: {nv - ov}"]
                self.stats[m] = nv
            nt = metrics[EventMetrics.CR_PROCESSED].value
            ot = self.stats.get(EventMetrics.CR_PROCESSED, 0)
            total = nt - ot
            self.stats[EventMetrics.CR_PROCESSED] = nt
            dt = t - self.last_ts
            if total:
                speed = total / dt
                self.logger.info(
                    "REPORT: %d events in %.2fms. %.2fev/s (%s)"
                    % (total, dt * 1000, speed, ", ".join(r))
                )
        self.last_ts = t

    rx_non_alpha = re.compile(r"[^a-z]+")
    rx_spaces = re.compile(r"\s+")

    def get_msg_codebook(self, s: str) -> str:
        """
        Generate message codebook vector
        """
        x = self.rx_non_alpha.sub(" ", s.lower())
        x = self.rx_spaces.sub(" ", x)
        return x.strip()

    @classmethod
    def is_codebook_match(cls, cb1: str, cb2: str):
        """
        Check codebooks for match
        """
        return cb1 == cb2

    def update_diagnostic(self, mo: ManagedObject, event: Event):
        """
        Update ManagedObject diagnostic
        Args:
            mo: Managed Object Instance
            event: Event Instance
        """
        # Check diagnostics
        if event.type.source == EventSource.SYSLOG and (
            SYSLOG_DIAG not in mo.diagnostics
            or mo.diagnostics[SYSLOG_DIAG]["state"] == DiagnosticState.unknown
        ):
            mo.diagnostic.set_state(
                diagnostic=SYSLOG_DIAG,
                state=DiagnosticState.enabled,
                reason=f"Receive Syslog from address: {event.target.address}",
                changed_ts=event.timestamp,
            )
        if event.type.source == EventSource.SNMP_TRAP and (
            SNMPTRAP_DIAG not in mo.diagnostics
            or mo.diagnostics[SNMPTRAP_DIAG]["state"] == DiagnosticState.unknown
        ):
            mo.diagnostic.set_state(
                diagnostic=SNMPTRAP_DIAG,
                state=DiagnosticState.enabled,
                reason=f"Receive Syslog from address: {event.target.address}",
                changed_ts=event.timestamp,
            )

    def register_event(
        self,
        event: Event,
        event_config: EventConfig,
        action: EventAction,
        resolved_vars: Dict[str, Any],
        mo: Optional[ManagedObject] = None,
        error: Optional[str] = None,
    ):
        """
        Send Event to Clickhouse (Archive)
        Args:
            event: Event instance
            event_config: Event Class
            action: Event Action
            resolved_vars: Processed event data
            mo: Managed Object mapping
            error: Error text on processed message
        """
        timestamp = event.timestamp
        data = {
            "date": timestamp.date(),
            "ts": timestamp.isoformat(),
            "start_ts": timestamp.isoformat(),
            #
            "event_id": str(event.id),
            "event_class": event_config.bi_id,
            "source": event.type.source.value,
            #
            "labels": event.labels or [],
            "data": orjson.dumps([d.to_json() for d in event.data]).decode(DEFAULT_ENCODING),
            "message": event.message or "",
            "severity": event.type.severity.value,
            "result_action": str(action.name),
            "error_message": error or "",
            #
            "raw_vars": {d.name: str(d.value) for d in event.data if d.name not in resolved_vars},
            "resolved_vars": {k: str(v) for k, v in resolved_vars.items()},
            "vars": {k: str(v) for k, v in event.vars.items()} if event_config else {},
            "snmp_trap_oid": event.type.id if event.type.source == EventSource.SNMP_TRAP else "",
            #
            "target": event.target.model_dump(exclude={"is_agent"}, exclude_none=True),
            "target_reference": event.target.reference,
            "target_name": event.target.name,
            "managed_object": None,
            "pool": None,
            "ip": None,
        }
        if event.target.address:
            data["ip"] = struct.unpack("!I", socket.inet_aton(event.target.address))[0]
        if mo:
            data.update(
                {
                    "managed_object": mo.bi_id,
                    "pool": mo.pool.bi_id,
                    "ip": struct.unpack("!I", socket.inet_aton(mo.address))[0],
                    "profile": mo.profile.bi_id,
                    "vendor": mo.vendor.bi_id if mo.vendor else None,
                    "platform": mo.platform.bi_id if mo.platform else None,
                    "version": mo.version.bi_id if mo.version else None,
                    "administrative_domain": mo.administrative_domain.bi_id,
                }
            )
        elif not mo and event.target.pool:
            p = Pool.get_by_name(event.target.pool)
            data["pool"] = p.bi_id
        if event.remote_system:
            rs = RemoteSystem.get_by_name(event.remote_system)
            data["remote_system"] = rs.bi_id
            data["remote_id"] = event.remote_id
        self.register_metrics("events", [data])

    async def on_event_rules_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.event_rules_ready_event.set()
        self.logger.info("%d Event Classification Rules has been loaded", self.ruleset.add_rules)

    async def update_rule(self, data: Dict[str, Any]) -> None:
        """Apply Classification Rules changes"""
        self.ruleset.update_rule(data)

    async def delete_rule(self, r_id: str) -> None:
        """Remove rules for ID"""
        self.ruleset.delete_rule(r_id)

    async def update_config(self, data: Dict[str, Any]) -> None:
        """Apply Event Config changes"""
        self.event_config[data["id"]] = EventConfig.from_config(data)
        if data["actions"]:
            self.action_set.update_rule(data["id"], data["actions"])
        self.add_configs += 1

    async def delete_config(self, ec_id: str) -> None:
        """Remove Event Config for ID"""
        if ec_id in self.event_config:
            del self.event_config[ec_id]
        self.action_set.delete_rule(ec_id)

    async def on_event_config_ready(self) -> None:
        """
        Called when all mappings are ready.
        """
        self.event_config_ready.set()
        self.logger.info("%d Event Configs has been loaded", self.add_configs)


if __name__ == "__main__":
    ClassifierService().start()
