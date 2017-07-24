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
from noc.fm.models.newevent import NewEvent
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventlog import EventLog
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.mib import MIB
from noc.fm.models.cloneclassificationrule import CloneClassificationRule
from noc.fm.models.enumeration import Enumeration
from noc.fm.models.eventtrigger import EventTrigger
from noc.inv.models.interfaceprofile import InterfaceProfile
import noc.inv.models.interface
from noc.core.profile.loader import loader as profile_loader
from noc.sa.models.managedobject import ManagedObject
from noc.lib.version import get_version
from noc.core.debug import error_report
from noc.lib.escape import fm_unescape
from noc.sa.interfaces.base import (IPv4Parameter, IPv6Parameter,
                                    IPParameter, IPv4PrefixParameter,
                                    IPv6PrefixParameter, PrefixParameter,
                                    MACAddressParameter, InterfaceTypeError)
from noc.lib.nosql import ObjectId
from noc.services.classifier.trigger import Trigger
from noc.services.classifier.exception import InvalidPatternException, EventProcessingFailed
from noc.services.classifier.cloningrule import CloningRule
from noc.services.classifier.rule import Rule
from noc.core.handler import get_handler
from noc.core.cache.base import cache

#
# Exceptions
#
#
# Patterns
#
rx_oid = re.compile(r"^(\d+\.){6,}$")

CR_FAILED = 0
CR_DELETED = 1
CR_SUPPRESSED = 2
CR_UNKNOWN = 3
CR_CLASSIFIED = 4
CR_DISPOSED = 5
CR_DUPLICATED = 6
CR_UDUPLICATED = 7
CR = ["failed", "deleted", "suppressed",
      "unknown", "classified", "disposed", "duplicated",
      "unk. duplicated"
      ]


class ClassifierService(Service):
    """
    Events-classification service
    """
    name = "classifier"
    leader_group_name = "classifier-%(pool)s"
    pooled = True
    DEFAULT_RULE = config.classifier.default_rule

    # SNMP OID pattern
    rx_oid = re.compile(r"^(\d+\.){6,}")

    interface_cache = TTLCache(maxsize=10000, ttl=60)

    def __init__(self):
        super(ClassifierService, self).__init__()
        self.version = get_version()
        self.rules = {}  # profile -> [rule, ..., rule]
        self.triggers = defaultdict(list)  # event_class_id -> [trigger1, ..., triggerN]
        self.templates = {}  # event_class_id -> (body_template,subject_template)
        self.post_process = {}  # event_class_id -> [rule1, ..., ruleN]
        self.enumerations = {}  # name -> value -> enumerated
        self.suppression = {}  # event_class_id -> (condition, suppress)
        self.alter_handlers = []
        self.unclassified_codebook_depth = 5
        self.unclassified_codebook = {}  # object id -> [<codebook>]
        self.handlers = {}  # event class id -> [<handler>]
        self.default_rule = None
        # Default link event action, when interface is not in inventory
        self.default_link_action = None
        # Lookup solution setup
        self.lookup_cls = None
        #
        self.last_ts = None
        self.stats = defaultdict(int)

    def on_activate(self):
        """
        Load rules from database after loading config
        """
        self.logger.info("Using rule lookup solution: %s",
                         config.classifier.lookup_handler)
        self.lookup_cls = get_handler(config.classifier.lookup_handler)
        self.load_enumerations()
        self.load_rules()
        self.load_triggers()
        self.load_suppression()
        self.load_link_action()
        self.load_handlers()
        self.subscribe(
            "events",
            "fmwriter",
            self.on_event
        )
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 1000, self.ioloop
        )
        report_callback.start()

    def load_rules(self):
        """
        Load rules from database
        """
        self.logger.info("Loading rules")
        n = 0
        cn = 0
        profiles = list(profile_loader.iter_profiles())
        self.rules = {}
        # Initialize profiles
        for p in profiles:
            self.rules[p] = {}
        # Load cloning rules
        cloning_rules = []
        for cr in CloneClassificationRule.objects.all():
            try:
                cloning_rules += [CloningRule(cr)]
            except InvalidPatternException as why:
                self.logger.error("Failed to load cloning rule '%s': Invalid pattern: %s", cr.name, why)
                continue
        self.logger.info("%d cloning rules found", len(cloning_rules))
        # Initialize rules
        for r in EventClassificationRule.objects.order_by("preference"):
            try:
                rule = Rule(self, r)
            except InvalidPatternException as why:
                self.logger.error("Failed to load rule '%s': Invalid patterns: %s", r.name, why)
                continue
            # Apply cloning rules
            rs = [rule]
            for cr in cloning_rules:
                if cr.match(rule):
                    try:
                        rs += [Rule(self, r, cr)]
                        cn += 1
                    except InvalidPatternException as why:
                        self.logger.error("Failed to clone rule '%s': Invalid patterns: %s", r.name, why)
                        continue
            for rule in rs:
                # Find profile restriction
                rx = re.compile(rule.profile)
                for p in profiles:
                    if rx.search(p):
                        if rule.chain not in self.rules[p]:
                            self.rules[p][rule.chain] = []
                        self.rules[p][rule.chain] += [rule]
                n += 1
        if cn:
            self.logger.info("%d rules are cloned", cn)
        self.default_rule = Rule(
            self,
            EventClassificationRule.objects.filter(name=self.DEFAULT_RULE).first()
        )
        # Apply lookup solution
        for p in self.rules:
            for c in self.rules[p]:
                self.rules[p][c] = self.lookup_cls(self.rules[p][c])
        self.logger.info("%d rules are loaded in the %d profiles",
                         n, len(self.rules))

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

    def load_enumerations(self):
        self.logger.info("Loading enumerations")
        n = 0
        self.enumerations = {}
        for e in Enumeration.objects.all():
            r = {}
            for k, v in e.values.items():
                for vv in v:
                    r[vv.lower()] = k
            self.enumerations[e.name] = r
            n += 1
        self.logger.info("%d enumerations loaded" % n)

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

    def decode_str(self, event, value):
        return value

    def decode_int(self, event, value):
        if value is not None and value.isdigit():
            return int(value)
        else:
            return 0

    def decode_ipv4_address(self, event, value):
        return IPv4Parameter().clean(value)

    def decode_ipv6_address(self, event, value):
        return IPv6Parameter().clean(value)

    def decode_ip_address(self, event, value):
        return IPParameter().clean(value)

    def decode_ipv4_prefix(self, event, value):
        return IPv4PrefixParameter().clean(value)

    def decode_ipv6_prefix(self, event, value):
        return IPv6PrefixParameter().clean(value)

    def decode_ip_prefix(self, event, value):
        return PrefixParameter().clean(value)

    def decode_mac(self, event, value):
        return MACAddressParameter().clean(value)

    def decode_interface_name(self, event, value):
        return event.managed_object.profile.convert_interface_name(value)

    def decode_oid(self, event, value):
        return value

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
        lookup = self.rules.get(event.managed_object.profile_name, {}).get(chain)
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

    def to_suppress(self, event, event_class, vars):
        """
        Check wrether event must be suppressed

        :returns: (bool, rule name, event)
        """
        ts = event.timestamp
        n_delta = None
        nearest = None
        n_name = None
        n_suppress = False
        for r, name, suppress in self.suppression[event_class.id]:
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

    def classify_event(self, event):
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
        resolved_vars = {
            "profile": event.managed_object.profile_name
        }
        if event.source == "SNMP Trap":
            # For SNMP traps format values according to MIB definitions
            resolved_vars.update(MIB.resolve_vars(event.raw_vars))
        elif event.source == "syslog" and not event.log:
            # Check for unclassified events flood
            o_id = event.managed_object.id
            if o_id in self.unclassified_codebook:
                msg = event.raw_vars.get("message", "")
                cb = self.get_msg_codebook(msg)
                for pcb in self.unclassified_codebook[o_id]:
                    if self.is_codebook_match(cb, pcb):
                        # Signature is already seen, suppress
                        return CR_UDUPLICATED
        # Find matched event class
        c_vars = event.raw_vars.copy()
        c_vars.update(dict((k, fm_unescape(resolved_vars[k])) for k in resolved_vars))
        rule, vars = self.find_matching_rule(event, c_vars)
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
            return CR_DELETED
        if rule.is_unknown_syslog:
            # Append codebook
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
        event_class = rule.event_class
        # Calculate rule variables
        vars = self.eval_rule_variables(event, event_class, vars)
        #
        self.logger.info(
            "[%s|%s|%s] Event class: %s (%s)",
            event.id, event.managed_object.name,
            event.managed_object.address, event_class.name, vars
        )
        # Additionally check link events
        disposable = True
        if event_class.link_event and "interface" in vars:
            if_name = event.managed_object.profile.convert_interface_name(vars["interface"])
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
                return CR_DELETED
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
                disposable = False
        # Deduplication
        if event_class.deduplication_window:
            de = self.find_duplicated_event(event, event_class, vars)
            if de:
                self.logger.info(
                    "[%s|%s|%s] Duplicates event %s. Discarding",
                    event.id, event.managed_object.name,
                    event.managed_object.address, de.id)
                de.log_message(
                    "Duplicated event %s has been discarded" % event.id
                )
                return CR_DUPLICATED
        # Suppress repeats
        if event_class.id in self.suppression:
            suppress, name, nearest = self.to_suppress(event, event_class,
                                                       vars)
            if suppress:
                self.logger.info(
                    "[%s|%s|%s] Suppressed by rule %s",
                    event.id, event.managed_object.name,
                    event.managed_object.address, name)
                # Update suppressing event
                nearest.log_suppression(event.timestamp)
                # Delete suppressed event
                return CR_SUPPRESSED
        # Activate event
        message = "Classified as '%s' by rule '%s'" % (event_class.name,
                                                       rule.name)
        log = event.log + [EventLog(timestamp=datetime.datetime.now(),
                                    from_status="N", to_status="A",
                                    message=message)]
        a_event = ActiveEvent(
            id=event.id,
            timestamp=event.timestamp,
            managed_object=event.managed_object,
            event_class=event_class,
            start_timestamp=event.timestamp,
            repeats=1,
            raw_vars=event.raw_vars,
            resolved_vars=resolved_vars,
            vars=vars,
            log=log,
            expires=event.timestamp + datetime.timedelta(seconds=event_class.ttl)
        )
        a_event.save()
        event = a_event
        # Call handlers
        if event_class.id in self.handlers:
            event_id = event.id
            for h in self.handlers[event_class.id]:
                try:
                    h(event)
                except:
                    error_report()
                if event.to_drop:
                    self.logger.info(
                        "[%s|%s|%s] Dropped by handler",
                        event.id, event.managed_object.name,
                        event.managed_object.address
                    )
                    event.id = event_id  # Restore event id
                    event.delete()
                    return CR_DELETED
        # Call triggers if necessary
        if event_class.id in self.triggers:
            event_id = event.id
            for t in self.triggers[event_class.id]:
                try:
                    t.call(event)
                except:
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
                    return CR_DELETED
        # Finally dispose event to further processing by correlator
        if disposable and rule.to_dispose:
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
                {"event_id": str(event.id)}
            )
            return CR_DISPOSED
        elif rule.is_unknown:
            return CR_UNKNOWN
        else:
            return CR_CLASSIFIED

    def find_duplicated_event(self, event, event_class, vars):
        """
        Returns duplicated event if exists
        """
        t0 = event.timestamp - datetime.timedelta(seconds=event_class.deduplication_window)
        q = {
            "managed_object": event.managed_object.id,
            "timestamp__gte": t0,
            "timestamp__lte": event.timestamp,
            "event_class": event_class.id,
            "id__ne": event.id
        }
        for v in vars:
            q["vars__%s" % v] = vars[v]
        return ActiveEvent.objects.filter(**q).first()

    def on_event(self, message, ts=None, object=None, data=None,
                 *args, **kwargs):
        event_id = bson.ObjectId()
        lag = (time.time() - ts) * 1000
        self.logger.debug("[%s] Receiving new event: %s (Lag: %.2fms)",
                          event_id, data, lag)
        mo = ManagedObject.get_by_id(object)
        if not mo:
            self.logger.info("[%s] Unknown managed object id %s. Skipping",
                             event_id, object)
            return True
        self.logger.info("[%s|%s|%s] Managed object found",
                         event_id, mo.name, mo.address)
        ne = NewEvent(
            id=event_id,
            timestamp=datetime.datetime.fromtimestamp(ts),
            managed_object=mo,
            raw_vars=data
        )
        try:
            s = self.classify_event(ne)
            self.stats[s] += 1
        except Exception as e:
            self.logger.error(
                "[%s|%s|%s] Failed to process event: %s",
                event_id, mo.name, mo.address, e)
            self.stats[CR_FAILED] += 1
            return False
        self.logger.info(
            "[%s|%s|%s] Event processed successfully",
            event_id, mo.name, mo.address
        )
        return True

    @tornado.gen.coroutine
    def report(self):
        t = self.ioloop.time()
        if self.last_ts:
            total = float(sum(v for v in self.stats.values()))
            dt = (t - self.last_ts)
            speed = total / dt
            if total:
                r = ", ".join(
                    "%s: %d" % (t, self.stats[i])
                    for i, t in enumerate(CR)
                )
                self.logger.info(
                    "REPORT: %d events in %.2fms. %.2fev/s (%s)" % (
                        total,
                        dt * 1000,
                        speed,
                        r
                    )
                )
        self.stats = defaultdict(int)
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
