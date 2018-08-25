#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Classifier service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import datetime
import os
from collections import defaultdict
import operator
import re
# Third-party modules
from cachetools import TTLCache, cachedmethod
import tornado.gen
import tornado.ioloop
import bson
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventlog import EventLog
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.mib import MIB
from noc.fm.models.eventtrigger import EventTrigger
from noc.inv.models.interfaceprofile import InterfaceProfile
import noc.inv.models.interface
from noc.sa.models.managedobject import ManagedObject
from noc.core.version import version
from noc.core.debug import error_report
from noc.lib.escape import fm_unescape
from noc.lib.nosql import ObjectId
from noc.services.classifier.trigger import Trigger
from noc.services.classifier.ruleset import RuleSet
from noc.core.cache.base import cache
from noc.core.perf import metrics
from noc.sa.interfaces.base import InterfaceTypeError
from noc.services.classifier.exception import EventProcessingFailed

# Patterns
rx_oid = re.compile(r"^(\d+\.){6,}$")

CR_FAILED = "events_failed"
CR_DELETED = "events_deleted"
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
    CR_UNKNOWN,
    CR_CLASSIFIED,
    CR_PREPROCESSED,
    CR_DISPOSED,
    CR_DUPLICATED,
    CR_UDUPLICATED,
    CR_UOBJECT
]

E_SRC_SYSLOG = "syslog"
E_SRC_SNMP_TRAP = "SNMP Trap"
E_SRC_SYSTEM = "system"
E_SRC_OTHER = "other"

E_SRC_METRICS = {
    E_SRC_SYSLOG: "events_syslog",
    E_SRC_SNMP_TRAP: "events_snmp_trap",
    E_SRC_SYSTEM: "events_system",
    E_SRC_OTHER: "events_other"
}


class ClassifierService(Service):
    """
    Events-classification service
    """
    name = "classifier"
    leader_group_name = "classifier-%(pool)s"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"

    # SNMP OID pattern
    rx_oid = re.compile(r"^(\d+\.){6,}")

    interface_cache = TTLCache(maxsize=10000, ttl=60)

    def __init__(self):
        super(ClassifierService, self).__init__()
        self.version = version.version
        self.ruleset = RuleSet()
        self.triggers = defaultdict(list)  # event_class_id -> [trigger1, ..., triggerN]
        self.templates = {}  # event_class_id -> (body_template,subject_template)
        self.post_process = {}  # event_class_id -> [rule1, ..., ruleN]
        self.suppression = {}  # event_class_id -> (condition, suppress)
        self.alter_handlers = []
        self.unclassified_codebook_depth = 5
        self.unclassified_codebook = {}  # object id -> [<codebook>]
        self.handlers = {}  # event class id -> [<handler>]
        # Default link event action, when interface is not in inventory
        self.default_link_action = None
        # Reporting
        self.last_ts = None
        self.stats = {}

    def on_activate(self):
        """
        Load rules from database after loading config
        """
        self.logger.info("Using rule lookup solution: %s",
                         config.classifier.lookup_handler)
        self.ruleset.load()
        self.load_triggers()
        self.load_suppression()
        self.load_link_action()
        self.load_handlers()
        self.subscribe(
            "events.%s" % config.pool,
            "fmwriter",
            self.on_event
        )
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 1000, self.ioloop
        )
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
                        t.handler and
                        t.condition == "True" and
                        t.selector is None and
                        t.time_pattern is None and
                        t.template is None and
                        t.notification_group is None
                    ):
                        # Alter handlers
                        self.alter_handlers += [
                            (c_id, t.is_enabled, t.handler)
                        ]
                    elif t.is_enabled:
                        # Register trigger
                        h = t.handler
                        if h:
                            h = self.resolve_handler(h)
                        if c_id in self.triggers:
                            self.triggers[c_id] += [Trigger(t, handler=h)]
                        else:
                            self.triggers[c_id] = [Trigger(t, handler=h)]
                        cn += 1
                        self.logger.debug("    %s", c_name)
            n += 1
        self.logger.info("%d triggers has been loaded to %d classes", n, cn)

    def load_suppression(self):
        """
        Load suppression rules
        """
        def compile_rule(s):
            """
            Compile suppression rule
            """
            x = [
                "'timestamp__gte': event.timestamp - datetime.timedelta(seconds=%d)" % s["window"],
                "'timestamp__lte': event.timestamp + datetime.timedelta(seconds=%d)" % s["window"]
            ]
            if len(s["event_class"]) == 1:
                x += ["'event_class': ObjectId('%s')" % s["event_class"][0]]
            else:
                x += ["'event_class__in: [%s]" % ", ".join(["ObjectId('%s')" % c for c in s["event_class"]])]
            for k, v in s["match_condition"].items():
                x += ["'%s': %s" % (k, v)]
            return compile("{%s}" % ", ".join(x), "<string>", "eval")

        self.logger.info("Loading suppression rules")
        self.suppression = {}
        for c in EventClass.objects.filter(repeat_suppression__exists=True):
            # Read event class rules
            suppression = []
            for r in c.repeat_suppression:
                to_skip = False
                for s in suppression:
                    if (
                        s["condition"] == r.condition and
                        s["window"] == r.window and
                        s["suppress"] == r.suppress and
                        s["match_condition"] == r.match_condition and
                        r.event_class.id not in s["event_class"]
                    ):
                        s["event_class"] += [r.event_class.id]
                        s["name"] += ", " + r.name
                        to_skip = True
                        break
                if to_skip:
                    continue
                suppression += [{
                    "name": r.name,
                    "condition": r.condition,
                    "window": r.window,
                    "suppress": r.suppress,
                    "match_condition": r.match_condition,
                    "event_class": [r.event_class.id]
                }]
            # Compile suppression rules
            self.suppression[c.id] = [
                (compile_rule(s), "%s::%s" % (c.name, s["name"]),
                 s["suppress"])
                for s in suppression]
        self.logger.info("Suppression rules are loaded")

    def load_link_action(self):
        self.default_link_action = None
        if config.classifier.default_interface_profile:
            p = InterfaceProfile.objects.filter(
                name=config.classifier.default_interface_profile).first()
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
                hh = self.resolve_handler(h)
                if hh:
                    hl += [hh]
            if hl:
                self.handlers[ec.id] = hl
        self.logger.info("Handlers are loaded")

    def resolve_handler(self, h):
        mn, s = h.rsplit(".", 1)
        try:
            m = __import__(mn, {}, {}, s)
        except ImportError:
            self.logger.error("Failed to load handler '%s'. Ignoring", h)
            return None
        try:
            return getattr(m, s)
        except AttributeError:
            self.logger.error("Failed to load handler '%s'. Ignoring", h)
            return None

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

    def find_matching_rule(self, event, vars):
        """
        Find first matching classification rule

        :param event: Event
        :type event: NewEvent
        :param vars: raw and resolved variables
        :type vars: dict
        :returns: Event class and extracted variables
        :rtype: tuple of (EventClass, dict)
        """
        # Get chain
        src = event.raw_vars.get("source")
        if src == "syslog":
            chain = "syslog"
            if "message" not in event.raw_vars:
                return None, None
        elif src == "SNMP Trap":
            chain = "snmp_trap"
        else:
            chain = "other"
        # Find rules lookup
        lookup = self.rules.get(event.managed_object.profile.name, {}).get(chain)
        if lookup:
            for r in lookup.lookup_rules(event, vars):
                # Try to match rule
                v = r.match(event, vars)
                if v is not None:
                    self.logger.debug(
                        "[%s] Matching class for event %s found: %s (Rule: %s)",
                        event.managed_object.name, event.id, r.event_class_name, r.name
                    )
                    return r, v
        if self.default_rule:
            return self.default_rule, {}
        return None, None

    def eval_rule_variables(self, event, event_class, vars):
        """
        Evaluate rule variables
        """
        r = {}
        for ecv in event_class.vars:
            # Check variable is present
            if ecv.name not in vars:
                if ecv.required:
                    raise Exception("Required variable '%s' is not found" % ecv.name)
                else:
                    continue
            # Decode variable
            v = vars[ecv.name]
            decoder = getattr(self, "decode_%s" % ecv.type, None)
            if decoder:
                try:
                    v = decoder(event, v)
                except InterfaceTypeError:
                    raise EventProcessingFailed("Cannot decode variable '%s'. Invalid %s: %s" % (ecv.name, ecv.type, repr(v)))
            r[ecv.name] = v
        return r

    def to_suppress(self, event, vars):
        """
        Check wrether event must be suppressed

        :returns: (bool, rule name, event)
        """
        ts = event.timestamp
        n_delta = None
        nearest = None
        n_name = None
        n_suppress = False
        for r, name, suppress in self.suppression[event.event_class.id]:
            q = eval(r, {}, {
                "event": event,
                "ObjectId": ObjectId,
                "datetime": datetime,
                "vars": vars
            })
            e = ActiveEvent.objects.filter(**q).order_by("-timestamp").first()
            if e:
                d = ts - e.timestamp
                if n_delta is None or d < n_delta:
                    n_delta = d
                    nearest = e
                    n_name = name
                    n_suppress = suppress
        return n_suppress, n_name, nearest

    @cachedmethod(operator.attrgetter("interface_cache"))
    def get_interface(self, managed_object_id, name):
        """
        Get interface instance
        """
        return noc.inv.models.interface.Interface.objects.filter(
            managed_object=managed_object_id,
            name=name
        ).first()

    def classify_event(self, event, data):
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
        resolved_vars = {
            "profile": event.managed_object.profile.name
        }
        if event.source == E_SRC_SNMP_TRAP:
            resolved_vars.update(MIB.resolve_vars(event.raw_vars))
        # Store event variables
        event.raw_vars = data
        event.resolved_vars = resolved_vars
        # Get matched event class
        if pre_event:
            # Event is preprocessed, get class and variables
            event_class_name = pre_event.get("class")
            event_class = EventClass.get_by_name(event_class_name)
            if not event_class:
                self.logger.error(
                    "[%s|%s|%s] Failed to process event: Invalid event class '%s'",
                    event.id, event.managed_object.name,
                    event.managed_object,
                    event_class_name
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
            c_vars.update(dict((k, fm_unescape(resolved_vars[k])) for k in resolved_vars))
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
                    event.id, event.managed_object.name,
                    event.managed_object.address
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
                cbs = cbs[:self.unclassified_codebook_depth]
                self.unclassified_codebook[o_id] = cbs
            self.logger.debug(
                "[%s|%s|%s] Matching rule: %s",
                event.id, event.managed_object.name,
                event.managed_object.address, rule.name
            )
            event.event_class = rule.event_class
            # Calculate rule variables
            event.vars = self.ruleset.eval_vars(event, event.event_class, vars)
            message = "Classified as '%s' by rule '%s'" % (event.event_class.name, rule.name)
            event.log += [EventLog(timestamp=datetime.datetime.now(),
                                   from_status="N", to_status="A",
                                   message=message)]
            is_unknown = rule.is_unknown
        # Event class found, process according to rules
        self.logger.info(
            "[%s|%s|%s] Event class: %s (%s)",
            event.id, event.managed_object.name,
            event.managed_object.address, event.event_class.name, event.vars
        )
        # Additionally check link events
        if self.check_link_event(event):
            return
        # Deduplication
        if self.deduplicate_event(event):
            return
        # Suppress repeats
        if self.suppress_repeats(event):
            return
        # Activate event
        event.expires = event.timestamp + datetime.timedelta(seconds=event.event_class.ttl)
        event.save()
        # Call handlers
        if self.call_event_handlers(event):
            return
        # Call triggers
        if self.call_event_triggers(event):
            return
        # Finally dispose event to further processing by correlator
        if event.to_dispose:
            self.dispose_event(event)
        if is_unknown:
            metrics[CR_UNKNOWN] += 1
        elif pre_event:
            metrics[CR_PREPROCESSED] += 1
        else:
            metrics[CR_CLASSIFIED] += 1

    def dispose_event(self, event):
        self.logger.info(
            "[%s|%s|%s] Disposing",
            event.id, event.managed_object.name,
            event.managed_object.address
        )
        # Heat up cache
        cache.set(
            "activeent-%s" % event.id,
            event,
            ttl=900
        )
        # @todo: Use config.pool instead
        self.pub(
            "correlator.dispose.%s" % event.managed_object.pool.name,
            {
                "event_id": str(event.id),
                "event": event.to_json()
            }
        )
        metrics[CR_DISPOSED] += 1

    def deduplicate_event(self, event):
        """
        Deduplicate event when necessary
        :param event:
        :param vars:
        :return: True, if event is duplication of existent one
        """
        dw = event.event_class.deduplication_window
        if not dw:
            return False  # No deduplication for event class
        t0 = event.timestamp - datetime.timedelta(seconds=dw)
        q = {
            "managed_object": event.managed_object.id,
            "timestamp__gte": t0,
            "timestamp__lte": event.timestamp,
            "event_class": event.event_class.id,
            "id__ne": event.id
        }
        for v in event.vars:
            q["vars__%s" % v] = event.vars[v]
        de = ActiveEvent.objects.filter(**q).first()
        if de:
            self.logger.info(
                "[%s|%s|%s] Duplicates event %s. Discarding",
                event.id, event.managed_object.name,
                event.managed_object.address, de.id)
            de.log_message(
                "Duplicated event %s has been discarded" % event.id
            )
            metrics[CR_DUPLICATED] += 1
            return True
        else:
            return False

    def suppress_repeats(self, event):
        """
        Suppress repeated events
        :param event:
        :param vars:
        :return:
        """
        if event.event_class.id not in self.suppression:
            return False
        suppress, name, nearest = self.to_suppress(event, event.vars)
        if suppress:
            self.logger.info(
                "[%s|%s|%s] Suppressed by rule %s",
                event.id, event.managed_object.name,
                event.managed_object.address, name)
            # Update suppressing event
            nearest.log_suppression(event.timestamp)
            # Delete suppressed event
            metrics[CR_SUPPRESSED] += 1
            return True
        else:
            return False

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
                    event.id, event.managed_object.name,
                    event.managed_object.address
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
                    event_id, event.managed_object.name,
                    event.managed_object.address, t.name
                )
                event.id = event_id  # Restore event id
                event.delete()
                metrics[CR_DELETED] += 1
                return True
        else:
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

    def check_link_event(self, event):
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
                event.id, event.managed_object.name,
                event.managed_object.address,
                iface.name
            )
            action = iface.profile.link_events
        else:
            self.logger.info(
                "[%s|%s|%s] Interface not found:%s",
                event.id, event.managed_object.name,
                event.managed_object.address, if_name
            )
            action = self.default_link_action
        if action == "I":
            # Ignore
            if iface:
                self.logger.info(
                    "[%s|%s|%s] Marked as ignored by interface profile '%s' (%s)",
                    event.id, event.managed_object.name,
                    event.managed_object.address,
                    iface.profile.name, iface.name)
            else:
                self.logger.info(
                    "[%s|%s|%s] Marked as ignored by default interface profile",
                    event.id, event.managed_object.name,
                    event.managed_object.address
                )
            metrics[CR_DELETED] += 1
            return True
        elif action == "L":
            # Do not dispose
            if iface:
                self.logger.info(
                    "[%s|%s|%s] Marked as not disposable by interface profile '%s' (%s)",
                    event.id, event.managed_object.name,
                    event.managed_object.address,
                    iface.profile.name, iface.name
                )
            else:
                self.logger.info(
                    "[%s|%s|%s] Marked as not disposable by default interface",
                    event.id, event.managed_object.name,
                    event.managed_object.address
                )
            event.do_not_dispose()
        return False

    def on_event(self, message, ts=None, object=None, data=None,
                 id=None, *args, **kwargs):
        event_ts = datetime.datetime.fromtimestamp(ts)
        # Generate or reuse existing object id
        event_id = bson.ObjectId(id)
        # Calculate messate processing delay
        lag = (time.time() - ts) * 1000
        metrics["lag_us"] = int(lag * 1000)
        self.logger.debug("[%s] Receiving new event: %s (Lag: %.2fms)",
                          event_id, data, lag)
        metrics[CR_PROCESSED] += 1
        # Resolve managed object
        mo = ManagedObject.get_by_id(object)
        if not mo:
            self.logger.info("[%s] Unknown managed object id %s. Skipping",
                             event_id, object)
            metrics[CR_UOBJECT] += 1
            return True
        self.logger.info("[%s|%s|%s] Managed object found",
                         event_id, mo.name, mo.address)
        # Process event
        source = data.pop("source", "other")
        event = ActiveEvent(
            id=event_id,
            timestamp=event_ts,
            start_timestamp=event_ts,
            managed_object=mo,
            source=source,
            repeats=1
        )  # raw_vars will be filled by classify_event()
        # Classify event
        try:
            self.classify_event(event, data)
        except Exception as e:
            self.logger.error(
                "[%s|%s|%s] Failed to process event: %s",
                event.id, mo.name, mo.address, e)
            metrics[CR_FAILED] += 1
            return False
        self.logger.info(
            "[%s|%s|%s] Event processed successfully",
            event.id, mo.name, mo.address
        )
        return True

    @tornado.gen.coroutine
    def report(self):
        t = self.ioloop.time()
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
            dt = (t - self.last_ts)
            if total:
                speed = total / dt
                self.logger.info(
                    "REPORT: %d events in %.2fms. %.2fev/s (%s)" % (
                        total,
                        dt * 1000,
                        speed,
                        ", ".join(r)
                    )
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


if __name__ == "__main__":
    ClassifierService().start()
