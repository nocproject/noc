#!./bin/python
# ---------------------------------------------------------------------
# Classifier service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import datetime
import os
from collections import defaultdict
import operator
import re
import socket
import struct
from time import perf_counter
from typing import Optional, Dict, List

# Third-party modules
import cachetools
from bson import ObjectId
import orjson

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventlog import EventLog
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.mib import MIB
from noc.fm.models.mibdata import MIBData
from noc.fm.models.eventtrigger import EventTrigger
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.main.models.label import Label
import noc.inv.models.interface
from noc.sa.models.managedobject import ManagedObject
from noc.core.version import version
from noc.core.debug import error_report
from noc.core.escape import fm_unescape
from noc.services.classifier.trigger import Trigger
from noc.services.classifier.ruleset import RuleSet
from noc.services.classifier.patternset import PatternSet
from noc.services.classifier.evfilter.dedup import DedupFilter
from noc.services.classifier.evfilter.suppress import SuppressFilter
from noc.services.classifier.abdetector import AbductDetector
from noc.core.perf import metrics
from noc.core.handler import get_handler
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.comp import smart_text, DEFAULT_ENCODING
from noc.core.msgstream.message import Message
from noc.core.mx import MX_LABELS, MX_H_VALUE_SPLITTER, MX_ADMINISTRATIVE_DOMAIN_ID
from noc.core.wf.diagnostic import SNMPTRAP_DIAG, SYSLOG_DIAG, DiagnosticState

# Patterns
rx_oid = re.compile(r"^(\d+\.){6,}$")

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

CR = [
    CR_FAILED,
    CR_DELETED,
    CR_SUPPRESSED,
    CR_IGNORED,
    CR_UNKNOWN,
    CR_CLASSIFIED,
    CR_PREPROCESSED,
    CR_DISPOSED,
    CR_DUPLICATED,
    CR_UDUPLICATED,
    CR_UOBJECT,
]

E_SRC_SYSLOG = "syslog"
E_SRC_SNMP_TRAP = "SNMP Trap"
E_SRC_SYSTEM = "system"
E_SRC_OTHER = "other"

E_SRC_MX_MESSAGE = {
    E_SRC_SYSLOG: "syslog",
    E_SRC_SNMP_TRAP: "snmptrap",
    E_SRC_SYSTEM: "system",
    E_SRC_OTHER: "other",
}

E_SRC_METRICS = {
    E_SRC_SYSLOG: "events_syslog",
    E_SRC_SNMP_TRAP: "events_snmp_trap",
    E_SRC_SYSTEM: "events_system",
    E_SRC_OTHER: "events_other",
}

NS = 1000000000.0

CABLE_ABDUCT = "Security | Abduct | Cable Abduct"

SNMP_TRAP_OID = "1__3__6__1__6__3__1__1__4__1__0"


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

    interface_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

    def __init__(self):
        super().__init__()
        self.version = version.version
        self.ruleset = RuleSet()
        self.patternset = PatternSet()
        self.triggers = defaultdict(list)  # event_class_id -> [trigger1, ..., triggerN]
        self.templates = {}  # event_class_id -> (body_template,subject_template)
        self.post_process = {}  # event_class_id -> [rule1, ..., ruleN]
        self.alter_handlers = []
        self.unclassified_codebook_depth = 5
        self.unclassified_codebook = {}  # object id -> [<codebook>]
        self.handlers = {}  # event class id -> [<handler>]
        self.dedup_filter = DedupFilter()
        self.suppress_filter = SuppressFilter()
        self.abduct_detector = AbductDetector()
        # Default link event action, when interface is not in inventory
        self.default_link_action = None
        # Reporting
        self.last_ts = None
        self.stats = {}
        #
        self.slot_number = 0
        self.total_slots = 0
        self.pool_partitions: Dict[str, int] = {}
        #
        self.cable_abduct_ecls: Optional[EventClass] = None

    async def on_activate(self):
        """
        Load rules from database after loading config
        """
        self.logger.info("Using rule lookup solution: %s", config.classifier.lookup_handler)
        self.ruleset.load()
        self.patternset.load()
        self.load_triggers()
        self.load_link_action()
        self.load_handlers()
        # Heat up MIB cache
        MIBData.preload()
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream(
            "events.%s" % config.pool,
            self.slot_number,
            self.on_event,
            async_cursor=config.classifier.allowed_async_cursor,
        )
        report_callback = PeriodicCallback(self.report, 1000)
        report_callback.start()

    def load_triggers(self):
        self.logger.info("Loading triggers")
        self.triggers = {}
        n = 0
        cn = 0
        self.alter_handlers = []
        ec = [(c.name, c.id) for c in EventClass.objects.all()]
        for t in EventTrigger.objects.all():
            self.logger.debug("Trigger '%s' for classes:", t.name)
            for c_name, c_id in ec:
                if re.search(t.event_class_re, c_name, re.IGNORECASE):
                    if (
                        t.handler
                        and t.condition == "True"
                        and t.resource_group is None
                        and t.time_pattern is None
                        and t.template is None
                        and t.notification_group is None
                    ):
                        # Alter handlers
                        self.alter_handlers += [(c_id, t.is_enabled, t.handler)]
                    elif t.is_enabled:
                        # Register trigger
                        h = t.handler
                        if h:
                            try:
                                h = get_handler(h)
                            except ImportError:
                                self.logger.error("Failed to load handler '%s'. Ignoring", h)
                                h = None
                        if c_id in self.triggers:
                            self.triggers[c_id] += [Trigger(t, handler=h)]
                        else:
                            self.triggers[c_id] = [Trigger(t, handler=h)]
                        cn += 1
                        self.logger.debug("    %s", c_name)
            n += 1
        self.logger.info("%d triggers has been loaded to %d classes", n, cn)

    def load_link_action(self):
        self.default_link_action = None
        if config.classifier.default_interface_profile:
            p = InterfaceProfile.objects.filter(
                name=config.classifier.default_interface_profile
            ).first()
            if p:
                self.logger.info("Setting default link event action to %s", p.link_events)
                self.default_link_action = p.link_events

    def load_handlers(self):
        self.logger.info("Loading handlers")
        self.handlers = {}
        # Process altered handlers
        enabled = defaultdict(list)  # event class id -> [handlers]
        disabled = defaultdict(list)  # event class id -> [handlers]
        for ec_id, status, handler in self.alter_handlers:
            if status:
                if handler in disabled[ec_id]:
                    disabled[ec_id].remove(handler)
                if handler not in enabled[ec_id]:
                    enabled[ec_id] += [handler]
            else:
                if handler not in disabled[ec_id]:
                    disabled[ec_id] += [handler]
                if handler in enabled[ec_id]:
                    enabled[ec_id].remove(handler)
        self.alter_handlers = []
        # Load handlers
        for ec in EventClass.objects.filter():
            handlers = (ec.handlers or []) + enabled[ec.id]
            if not handlers:
                continue
            self.logger.debug("    <%s>: %s", ec.name, ", ".join(handlers))
            hl = []
            for h in handlers:
                if h in disabled[ec.id]:
                    self.logger.debug("        disabling handler %s", h)
                    continue
                # Resolve handler
                try:
                    hh = get_handler(h)
                    hl += [hh]
                except ImportError:
                    self.logger.error("Failed to load handler '%s'. Ignoring", h)
            if hl:
                self.handlers[ec.id] = hl
        self.logger.info("Handlers are loaded")

    def retry_failed_events(self):
        """
        Return failed events to the unclassified queue if
        failed on other version of classifier
        """
        if FailedEvent.objects.count() == 0:
            return
        self.logger.info("Recovering failed events")
        wm = datetime.datetime.now() - datetime.timedelta(seconds=86400)  # @todo: use config
        dc = FailedEvent.objects.filter(timestamp__lt=wm).count()
        if dc > 0:
            self.logger.info("%d failed events are deprecated and removed", dc)
            FailedEvent.objects.filter(timestamp__lt=wm).delete()
        for e in FailedEvent.objects.filter(version__ne=self.version):
            e.mark_as_new("Reclassification has been requested by noc-classifer")
            self.logger.debug("Failed event %s has been recovered", e.id)

    @staticmethod
    def get_managed_object_mx(o: "ManagedObject"):
        r = {
            "id": str(o.id),
            "bi_id": str(o.bi_id),
            "name": o.name,
            "administrative_domain": {
                "id": o.administrative_domain.id,
                "name": o.administrative_domain.name,
            },
            "labels": [
                ll
                for ll in Label.objects.filter(
                    name__in=o.labels, expose_datastream=True
                ).values_list("name")
            ],
        }
        if o.remote_system:
            r["remote_system"] = {
                "id": str(o.remote_system.id),
                "name": o.remote_system.name,
            }
            r["remote_id"] = o.remote_id
        if o.administrative_domain.remote_system:
            r["administrative_domain"]["remote_system"] = {
                "id": str(o.administrative_domain.remote_system.id),
                "name": o.administrative_domain.remote_system.name,
            }
            r["administrative_domain"]["remote_id"] = o.administrative_domain.remote_id
        return r

    async def register_mx_message(
        self, event: "ActiveEvent", resolved_raws: Optional[List[Dict[str, str]]]
    ):
        """
        Send event message to MX service
        :param event:
        :param resolved_raws: Raw variables for 'SNMP Trap' event
        :return:
        """
        metrics["events_message"] += 1
        self.logger.debug(
            "[%s|%s|%s] Register MX message",
            event.id,
            event.managed_object.name,
            event.managed_object.address,
        )
        msg = {
            "timestamp": event.timestamp,
            "message_id": event.raw_vars.get("message_id"),
            "collector_type": E_SRC_MX_MESSAGE[event.source],
            "collector": event.raw_vars.get("collector"),
            "address": event.raw_vars.get("source_address"),
            "managed_object": self.get_managed_object_mx(event.managed_object),
            "event_class": {"id": str(event.event_class.id), "name": event.event_class.name},
            "event_vars": event.vars,
        }
        if event.source == E_SRC_SYSLOG:
            msg["data"] = {
                "facility": event.raw_vars.get("facility", ""),
                "severity": event.raw_vars.get("severity", ""),
                "message": event.raw_vars.get("message", ""),
            }
        elif event.source == E_SRC_SNMP_TRAP:
            msg["data"] = {"vars": resolved_raws}
        else:
            msg["data"] = event.raw_vars
        # Register MX message
        await self.send_message(
            message_type="event",
            data=orjson.dumps(msg),
            sharding_key=int(event.managed_object.id),
            headers={
                MX_LABELS: MX_H_VALUE_SPLITTER.join(event.managed_object.effective_labels).encode(
                    DEFAULT_ENCODING
                ),
                MX_ADMINISTRATIVE_DOMAIN_ID: str(
                    event.managed_object.administrative_domain.id
                ).encode(DEFAULT_ENCODING),
            },
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("interface_cache"))
    def get_interface(cls, managed_object_id, name):
        """
        Get interface instance
        """
        return noc.inv.models.interface.Interface.objects.filter(
            managed_object=managed_object_id, name=name
        ).first()

    async def classify_event(self, event, data):
        """
        Perform event classification.
        Classification steps are:

        1. Format SNMP values accordind to MIB definitions (for SNMP events only)
        2. Find matching classification rule
        3. Calculate rule variables

        :param event: Event to classify
        :type event: NewEvent
        :returns: Classification status (CR_*)
        """
        metrics[E_SRC_METRICS.get(event.source, E_SRC_OTHER)] += 1
        is_unknown = False
        #
        pre_event = data.pop("$event", None)
        # Resolve MIB variables for SNMP Traps
        resolved_vars = {"profile": event.managed_object.profile.name}
        # Store event variables
        event.raw_vars = data
        resoved_raws = None
        if config.message.enable_event and event.source == E_SRC_SNMP_TRAP:
            resolved_vars.update(MIB.resolve_vars(event.raw_vars, include_raw=True))
            resoved_raws = resolved_vars.pop("raw")
        elif event.source == E_SRC_SNMP_TRAP:
            resolved_vars.update(MIB.resolve_vars(event.raw_vars))
        event.resolved_vars = resolved_vars
        # Get matched event class
        if pre_event:
            # Event is preprocessed, get class and variables
            event_class_name = pre_event.get("class")
            event_class = EventClass.get_by_name(event_class_name)
            if not event_class:
                self.logger.error(
                    "[%s|%s|%s] Failed to process event: Invalid event class '%s'",
                    event.id,
                    event.managed_object.name,
                    event.managed_object,
                    event_class_name,
                )
                metrics[CR_FAILED] += 1
                return  # Drop malformed message
            event.event_class = event_class
            event.vars = pre_event.get("vars", {})
        else:
            # Prevent unclassified events flood
            if self.check_unclassified_syslog_flood(event):
                return
            # Find matched event class
            c_vars = event.raw_vars.copy()
            c_vars.update({k: smart_text(fm_unescape(resolved_vars[k])) for k in resolved_vars})
            rule, vars = self.ruleset.find_rule(event, c_vars)
            if rule is None:
                # Something goes wrong.
                # No default rule found. Exit immediately
                self.logger.error("No default rule found. Exiting")
                os._exit(1)
            if rule.to_drop:
                # Silently drop event if declared by action
                self.logger.info(
                    "[%s|%s|%s] Dropped by action",
                    event.id,
                    event.managed_object.name,
                    event.managed_object.address,
                )
                metrics[CR_DELETED] += 1
                return
            if rule.is_unknown_syslog:
                # Append to codebook
                msg = event.raw_vars.get("message", "")
                cb = self.get_msg_codebook(msg)
                o_id = event.managed_object.id
                if o_id not in self.unclassified_codebook:
                    self.unclassified_codebook[o_id] = []
                cbs = [cb] + self.unclassified_codebook[o_id]
                cbs = cbs[: self.unclassified_codebook_depth]
                self.unclassified_codebook[o_id] = cbs
            self.logger.debug(
                "[%s|%s|%s] Matching rule: %s",
                event.id,
                event.managed_object.name,
                event.managed_object.address,
                rule.name,
            )
            event.event_class = rule.event_class
            # Calculate rule variables
            event.vars = self.ruleset.eval_vars(event, event.event_class, vars)
            message = f"Classified as '{event.event_class.name}' by rule '{rule.name}'"
            event.log += [
                EventLog(
                    timestamp=datetime.datetime.now(),
                    from_status="N",
                    to_status="A",
                    message=message,
                )
            ]
            is_unknown = rule.is_unknown
        # Event class found, process according to rules
        self.logger.info(
            "[%s|%s|%s] Event class: %s (%s)",
            event.id,
            event.managed_object.name,
            event.managed_object.address,
            event.event_class.name,
            event.vars,
        )
        # Deduplication
        if self.deduplicate_event(event):
            return
        # Suppress repeats
        if self.suppress_repeats(event):
            return
        # Activate event
        event.expires = event.timestamp + datetime.timedelta(seconds=event.event_class.ttl)

        # Send event to clickhouse
        mo = event.managed_object
        data = {
            "date": event.timestamp.date(),
            "ts": event.timestamp,
            "start_ts": event.start_timestamp,
            "event_id": str(event.id),
            "event_class": event.event_class.bi_id,
            "source": event.source or E_SRC_OTHER,
            "raw_vars": {k: str(v) for k, v in event.raw_vars.items()},
            "resolved_vars": {k: str(v) for k, v in event.resolved_vars.items()},
            "vars": {k: str(v) for k, v in event.vars.items()},
            "snmp_trap_oid": event.raw_vars.get(SNMP_TRAP_OID, ""),
            "message": event.raw_vars.get("message", ""),
            "managed_object": mo.bi_id,
            "pool": mo.pool.bi_id,
            "ip": struct.unpack("!I", socket.inet_aton(mo.address))[0],
            "profile": mo.profile.bi_id,
            "vendor": mo.vendor.bi_id if mo.vendor else None,
            "platform": mo.platform.bi_id if mo.platform else None,
            "version": mo.version.bi_id if mo.version else None,
            "administrative_domain": mo.administrative_domain.bi_id,
        }
        self.register_metrics("events", [data])

        # Fill deduplication filter
        self.dedup_filter.register(event)
        # Fill suppress filter
        self.suppress_filter.register(event)
        if config.message.enable_event:
            await self.register_mx_message(event, resoved_raws)
        # Call handlers
        if self.call_event_handlers(event):
            return
        # Additionally check link events
        if await self.check_link_event(event):
            return
        # Call triggers
        if self.call_event_triggers(event):
            return
        # Finally dispose event to further processing by correlator
        if event.to_dispose:
            await self.dispose_event(event)
        if is_unknown:
            metrics[CR_UNKNOWN] += 1
        elif pre_event:
            metrics[CR_PREPROCESSED] += 1
        else:
            metrics[CR_CLASSIFIED] += 1

    async def dispose_event(self, event):
        self.logger.info(
            "[%s|%s|%s] Disposing",
            event.id,
            event.managed_object.name,
            event.managed_object.address,
        )
        # Calculate partition
        fm_pool = event.managed_object.get_effective_fm_pool().name
        stream = f"dispose.{fm_pool}"
        num_partitions = self.pool_partitions.get(fm_pool)
        if not num_partitions:
            num_partitions = await self.get_stream_partitions(stream)
            self.pool_partitions[fm_pool] = num_partitions
        partition = int(event.managed_object.id) % num_partitions
        self.publish(
            orjson.dumps({"$op": "event", "event_id": str(event.id), "event": event.to_json()}),
            stream=stream,
            partition=partition,
        )
        metrics[CR_DISPOSED] += 1

    def deduplicate_event(self, event: ActiveEvent) -> bool:
        """
        Deduplicate event when necessary
        :param event:
        :param vars:
        :return: True, if event is duplication of existent one
        """
        de_id = self.dedup_filter.find(event)
        if not de_id:
            return False
        self.logger.info(
            "[%s|%s|%s] Duplicates event %s. Discarding",
            event.id,
            event.managed_object.name,
            event.managed_object.address,
            de_id,
        )
        # de.log_message("Duplicated event %s has been discarded" % event.id)
        metrics[CR_DUPLICATED] += 1
        return True

    def suppress_repeats(self, event: ActiveEvent) -> bool:
        """
        Suppress repeated events
        :param event:
        :param vars:
        :return:
        """
        se_id = self.suppress_filter.find(event)
        if not se_id:
            return False
        self.logger.info(
            "[%s|%s|%s] Suppressed by event %s",
            event.id,
            event.managed_object.name,
            event.managed_object.address,
            se_id,
        )
        # Update suppressing event
        ActiveEvent.log_suppression(se_id, event.timestamp)
        # Delete suppressed event
        metrics[CR_SUPPRESSED] += 1
        return True

    def call_event_handlers(self, event):
        """
        Call handlers associated with event class
        :param event:
        :return:
        """
        if event.event_class.id not in self.handlers:
            return False
        event_id = event.id  # Temporary store id
        for h in self.handlers[event.event_class.id]:
            try:
                h(event)
            except Exception:
                error_report()
            if event.to_drop:
                self.logger.info(
                    "[%s|%s|%s] Dropped by handler",
                    event.id,
                    event.managed_object.name,
                    event.managed_object.address,
                )
                event.id = event_id  # Restore event id
                event.delete()
                metrics[CR_DELETED] += 1
                return True
        return False

    def call_event_triggers(self, event):
        """
        Call triggers associated with event class
        :param event:
        :return:
        """
        if event.event_class.id not in self.triggers:
            return False
        event_id = event.id
        for t in self.triggers[event.event_class.id]:
            try:
                t.call(event)
            except Exception:
                error_report()
            if event.to_drop:
                # Delete event and stop processing
                self.logger.info(
                    "[%s|%s|%s] Dropped by trigger %s",
                    event_id,
                    event.managed_object.name,
                    event.managed_object.address,
                    t.name,
                )
                event.id = event_id  # Restore event id
                event.delete()
                metrics[CR_DELETED] += 1
                return True
        return False

    def check_unclassified_syslog_flood(self, event):
        """
        Check if incoming messages is in unclassified codebook
        :param event:
        :return:
        """
        if event.source != E_SRC_SYSLOG or len(event.log):
            return False
        pcbs = self.unclassified_codebook.get(event.managed_object.id)
        if not pcbs:
            return False
        msg = event.raw_vars.get("message", "")
        cb = self.get_msg_codebook(msg)
        for pcb in pcbs:
            if self.is_codebook_match(cb, pcb):
                # Signature is already seen, suppress
                metrics[CR_UDUPLICATED] += 1
                return True
        return False

    async def check_link_event(self, event):
        """
        Additional link events check
        :param event:
        :return: True - stop processing, False - continue
        """
        if not event.event_class.link_event or "interface" not in event.vars:
            return False
        if_name = event.managed_object.get_profile().convert_interface_name(event.vars["interface"])
        iface = self.get_interface(event.managed_object.id, if_name)
        if iface:
            self.logger.info(
                "[%s|%s|%s] Found interface %s",
                event.id,
                event.managed_object.name,
                event.managed_object.address,
                iface.name,
            )
            action = iface.profile.link_events
        else:
            self.logger.info(
                "[%s|%s|%s] Interface not found:%s",
                event.id,
                event.managed_object.name,
                event.managed_object.address,
                if_name,
            )
            action = self.default_link_action
        # Abduct detection
        link_status = event.get_hint("link_status")
        if (
            link_status is not None
            and iface
            and iface.profile.enable_abduct_detection
            and event.managed_object.object_profile.abduct_detection_window
            and event.managed_object.object_profile.abduct_detection_threshold
        ):
            ts = int(event.timestamp.timestamp())
            if link_status:
                self.abduct_detector.register_up(ts, iface)
            else:
                if self.abduct_detector.register_down(ts, iface):
                    await self.raise_abduct_event(event)
        # Link actions
        if action == "I":
            # Ignore
            if iface:
                self.logger.info(
                    "[%s|%s|%s] Marked as ignored by interface profile '%s' (%s)",
                    event.id,
                    event.managed_object.name,
                    event.managed_object.address,
                    iface.profile.name,
                    iface.name,
                )
            else:
                self.logger.info(
                    "[%s|%s|%s] Marked as ignored by default interface profile",
                    event.id,
                    event.managed_object.name,
                    event.managed_object.address,
                )
            metrics[CR_DELETED] += 1
            return True
        elif action == "L":
            # Do not dispose
            if iface:
                self.logger.info(
                    "[%s|%s|%s] Marked as not disposable by interface profile '%s' (%s)",
                    event.id,
                    event.managed_object.name,
                    event.managed_object.address,
                    iface.profile.name,
                    iface.name,
                )
            else:
                self.logger.info(
                    "[%s|%s|%s] Marked as not disposable by default interface",
                    event.id,
                    event.managed_object.name,
                    event.managed_object.address,
                )
            event.do_not_dispose()
        return False

    async def on_event(self, msg: Message):
        # Decode message
        event = orjson.loads(msg.value)
        object = event.get("object")
        data = event.get("data")
        # Process event
        event_ts = datetime.datetime.fromtimestamp(event.get("ts"))
        # Generate or reuse existing object id
        event_id = ObjectId(event.get("id"))
        # Calculate message processing delay
        lag = (time.time() - float(msg.timestamp) / NS) * 1000
        metrics["lag_us"] = int(lag * 1000)
        self.logger.debug("[%s] Receiving new event: %s (Lag: %.2fms)", event_id, data, lag)
        metrics[CR_PROCESSED] += 1
        # Resolve managed object
        mo = ManagedObject.get_by_id(object)
        if not mo:
            self.logger.info("[%s] Unknown managed object id %s. Skipping", event_id, object)
            metrics[CR_UOBJECT] += 1
            return
        self.logger.info("[%s|%s|%s] Managed object found", event_id, mo.name, mo.address)
        # Process event
        source = data.pop("source", "other")
        # Check diagnostics
        if source == E_SRC_SYSLOG and (
            SYSLOG_DIAG not in mo.diagnostics
            or mo.diagnostics[SYSLOG_DIAG]["state"] == DiagnosticState.unknown
        ):
            mo.diagnostic.set_state(
                diagnostic=SYSLOG_DIAG,
                state=DiagnosticState.enabled,
                reason=f"Receive Syslog from address: {data.get('source_address')}",
                changed_ts=event_ts,
            )
        if source == E_SRC_SNMP_TRAP and (
            SNMPTRAP_DIAG not in mo.diagnostics
            or mo.diagnostics[SNMPTRAP_DIAG]["state"] == DiagnosticState.unknown
        ):
            mo.diagnostic.set_state(
                diagnostic=SNMPTRAP_DIAG,
                state=DiagnosticState.enabled,
                reason=f"Receive Syslog from address: {data.get('source_address')}",
                changed_ts=event_ts,
            )

        event = ActiveEvent(
            id=event_id,
            timestamp=event_ts,
            start_timestamp=event_ts,
            managed_object=mo,
            source=source,
            repeats=1,
        )  # raw_vars will be filled by classify_event()
        # Ignore event
        if self.patternset.find_ignore_rule(event, data):
            self.logger.debug(
                "[%s|%s|%s] Ignored event %s vars %s", event_id, mo.name, mo.address, event, data
            )
            metrics[CR_IGNORED] += 1
            return
        # Classify event
        try:
            await self.classify_event(event, data)
        except Exception as e:
            self.logger.error(
                "[%s|%s|%s] Failed to process event: %s", event.id, mo.name, mo.address, e
            )
            metrics[CR_FAILED] += 1
            return
        self.logger.info("[%s|%s|%s] Event processed successfully", event.id, mo.name, mo.address)

    async def report(self):
        t = perf_counter()
        if self.last_ts:
            r = []
            for m in CR:
                ov = self.stats.get(m, 0)
                nv = metrics[m].value
                r += ["%s: %d" % (m[7:], nv - ov)]
                self.stats[m] = nv
            nt = metrics[CR_PROCESSED].value
            ot = self.stats.get(CR_PROCESSED, 0)
            total = nt - ot
            self.stats[CR_PROCESSED] = nt
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

    def get_msg_codebook(self, s):
        """
        Generate message codebook vector
        """
        x = self.rx_non_alpha.sub(" ", s.lower())
        x = self.rx_spaces.sub(" ", x)
        return x.strip()

    def is_codebook_match(self, cb1, cb2):
        """
        Check codebooks for match
        """
        return cb1 == cb2

    async def raise_abduct_event(self, event: ActiveEvent) -> None:
        """
        Create Cable Abduct Event and dispose it to correlator
        :param event:
        :return:
        """
        if not self.cable_abduct_ecls:
            self.cable_abduct_ecls = EventClass.get_by_name(CABLE_ABDUCT)
        abd_event = ActiveEvent(
            timestamp=event.timestamp,
            start_timestamp=event.timestamp,
            managed_object=event.managed_object,
            source=event.source,
            repeats=1,
            event_class=self.cable_abduct_ecls,
        )
        abd_event.save()
        await self.dispose_event(abd_event)


if __name__ == "__main__":
    ClassifierService().start()
