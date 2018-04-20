# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-classifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import time
import datetime
import sys
import os
from collections import defaultdict
import operator
## Django modules
from django.db import reset_queries
## Third-party modules
import mongoengine.connection
from cachetools import TTLCache, cachedmethod
## NOC modules
from noc.lib.daemon import Daemon
from noc.fm.models.newevent import NewEvent
from noc.fm.models.failedevent import FailedEvent
from noc.fm.models import (EventClassificationRule,
                           EventClass, MIB, EventLog, CloneClassificationRule,
                           ActiveEvent, EventTrigger, Enumeration)
from noc.fm.models.ignorepattern import IgnorePattern
from noc.inv.models import InterfaceProfile
from noc.fm.correlator.scheduler import CorrelatorScheduler
import noc.inv.models
from noc.sa.models import profile_registry
from noc.sa.models.collector import Collector
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.objectmap import ObjectMap
from noc.lib.version import get_version
from noc.lib.debug import format_frames, get_traceback_frames, error_report
from noc.lib.escape import fm_unescape
from noc.sa.interfaces.base import (IPv4Parameter, IPv6Parameter,
                                    IPParameter, IPv4PrefixParameter,
                                    IPv6PrefixParameter, PrefixParameter,
                                    MACAddressParameter, InterfaceTypeError)
from noc.lib.nosql import ObjectId
from noc.lib.dateutils import total_seconds
from trigger import Trigger
from exception import InvalidPatternException, EventProcessingFailed
from cloningrule import CloningRule
from rule import Rule
from noc.lib.solutions import get_event_class_handlers, get_solution

##
## Exceptions
##
##
## Patterns
##
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


class Classifier(Daemon):
    """
    noc-classifier daemon
    """
    daemon_name = "noc-classifier"
    DEFAULT_RULE = "Unknown | Default"

    # SNMP OID pattern
    rx_oid = re.compile(r"^(\d+\.){6,}")

    interface_cache = TTLCache(maxsize=10000, ttl=60)

    def __init__(self):
        self.version = get_version()
        self.rules = {}  # profile -> [rule, ..., rule]
        self.triggers = {}  # event_class_id -> [trigger1, ..., triggerN]
        self.templates = {}  # event_class_id -> (body_template,subject_template)
        self.post_process = {}  # event_class_id -> [rule1, ..., ruleN]
        self.enumerations = {}  # name -> value -> enumerated
        self.suppression = {}  # event_class_id -> (condition, suppress)
        self.dump_clone = False
        self.deduplication_window = 0
        self.unclassified_codebook_depth = 5
        self.unclassified_codebook = {}  # object id -> [<codebook>]
        self.handlers = {}  # event class id -> [<handler>]
        self.default_rule = None
        # Default link event action, when interface is not in inventory
        self.default_link_action = None
        self.is_distributed = False
        self.collector_id = None
        # Lookup solution setup
        self.lookup_cls = None
        Daemon.__init__(self)
        self.logger.info("Running Classifier version %s", self.version)
        self.correlator_scheduler = CorrelatorScheduler()

    def setup_opt_parser(self):
        self.opt_parser.add_option("-d", "--dump", action="append",
                                   dest="dump")

    def load_config(self):
        """
        Load rules from database after loading config
        """
        self.dump_clone = (self.options.dump is not None and
                           "clone" in self.options.dump)
        super(Classifier, self).load_config()
        self.deduplication_window = self.config.getint(
            "classifier", "deduplication_window")
        lsn = self.config.get("classifier", "lookup_solution")
        self.logger.info("Using rule lookup solution: %s", lsn)
        self.lookup_cls = get_solution(lsn)
        self.load_enumerations()
        self.load_rules()
        self.load_triggers()
        self.load_suppression()
        self.load_link_action()
        self.load_handlers()
        self.is_distributed = self.config.getboolean("collector", "enabled")
        if self.is_distributed:
            self.setup_distributed_mode()

    def load_rules(self):
        """
        Load rules from database
        """
        self.logger.info("Loading rules")
        n = 0
        cn = 0
        profiles = list(profile_registry.classes)
        self.rules = {}
        # Initialize profiles
        for p in profiles:
            self.rules[p] = {}
        # Load cloning rules
        cloning_rules = []
        for cr in CloneClassificationRule.objects.all():
            try:
                cloning_rules += [CloningRule(cr)]
            except InvalidPatternException, why:
                self.logger.error("Failed to load cloning rule '%s': Invalid pattern: %s", cr.name, why)
                continue
        self.logger.info("%d cloning rules found", len(cloning_rules))
        # Initialize rules
        for r in EventClassificationRule.objects.order_by("preference"):
            try:
                rule = Rule(self, r)
            except InvalidPatternException, why:
                self.logger.error("Failed to load rule '%s': Invalid patterns: %s", r.name, why)
                continue
            # Apply cloning rules
            rs = [rule]
            for cr in cloning_rules:
                if cr.match(rule):
                    try:
                        rs += [Rule(self, r, cr)]
                        cn += 1
                    except InvalidPatternException, why:
                        self.logger.error("Failed to clone rule '%s': Invalid patterns: %s", r.name, why)
                        continue
            for rule in rs:
                # Find profile restriction
                if rule.profile:
                    profile_re = rule.profile
                else:
                    profile_re = r"^.*$"
                rx = re.compile(profile_re)
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
        ec = [(c.name, c.id) for c in EventClass.objects.all()]
        for t in EventTrigger.objects.filter(is_enabled=True):
            self.logger.debug("Trigger '%s' for classes:", t.name)
            for c_name, c_id in ec:
                if re.search(t.event_class_re, c_name, re.IGNORECASE):
                    try:
                        self.triggers[c_id] += [Trigger(t)]
                    except KeyError:
                        self.triggers[c_id] = [Trigger(t)]
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
                    if (s["condition"] == r.condition and
                        s["window"] == r.window and
                        s["suppress"] == r.suppress and
                        s["match_condition"] == r.match_condition):
                        if r.event_class.id not in s["event_class"]:
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
            self.suppression[c.id] = [(compile_rule(s),
                                       "%s::%s" % (c.name, s["name"]),
                                       s["suppress"])
                for s in suppression]
        self.logger.info("Suppression rules are loaded")

    def load_link_action(self):
        self.default_link_action = None
        profile_name = self.config.get(
            "classifier", "default_interface_profile").strip()
        if profile_name:
            p = InterfaceProfile.objects.filter(name=profile_name).first()
            if p:
                self.logger.info("Setting default link event action to %s", p.link_events)
                self.default_link_action = p.link_events

    def load_handlers(self):
        self.logger.info("Loading handlers")
        self.handlers = {}
        for ec in EventClass.objects.filter():
            handlers = get_event_class_handlers(ec)
            if not handlers:
                continue
            self.logger.debug("    <%s>: %s", ec.name, ", ".join(handlers))
            hl = []
            for h in ec.handlers:
                # Resolve handler
                hh = self.resolve_handler(h)
                if hh:
                    hl += [hh]
            if hl:
                self.handlers[ec.id] = hl
        self.logger.info("Handlers are loaded")

    def setup_distributed_mode(self):
        if "collector" in mongoengine.connection._connection_settings:
            return
        self.logger.info("Entering distributed mode")
        # Get collector id
        collector_name = self.config.get("collector", "name")
        if not collector_name:
            self.logger.error("Collector name missed. Exiting")
            os._exit(1)
        try:
            self.collector_id = Collector.objects.get(name=collector_name).id
        except Collector.DoesNotExist:
            self.logger.error("Invalid collector name: '%s'. Exiting", collector_name)
            os._exit(1)
        # Connect to collector's database
        mongoengine.connection.register_connection(
            "collector",
            name=self.config.get("collector_database", "name"),
            host=self.config.get("collector_database", "host") or "127.0.0.1",
            port=self.config.getint("collector_database", "port") or 27017,
            username=self.config.get("collector_database", "user") or None,
            password=self.config.get("collector_database", "password") or None
        )
        # Switch new and failed events collections to collector database
        NewEvent._meta["db_alias"] = "collector"
        FailedEvent._meta["db_alias"] = "collector"

    @classmethod
    def resolve_handler(cls, h):
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

    def update_object_map(self):
        self.logger.debug("Updating object maps")
        d = ObjectMap.get_map(self.collector_id)
        cdb = mongoengine.connection.get_db("collector")
        n = self.config.get("collector_database", "object_map")
        ntmp = n + "_tmp"
        cdb.drop_collection(ntmp)
        tmp = cdb[ntmp]
        if d:
            tmp.insert(d, safe=True)
            tmp.rename(n, dropTarget=True)
        cdb[n].ensure_index("sources")
        self.logger.debug("Updating ignore rules")
        im = cdb[self.config.get("collector_database", "ignore_map")]
        i_patterns = defaultdict(list)
        for p in IgnorePattern.objects.filter(is_active=True):
            try:
                re.compile(p.pattern)
                i_patterns[p.source] += [p.pattern]
            except re.error, why:
                self.logger.error("Invalid ignore pattern '%s' (%s)",
                    p.pattern, why)
        # Update patterns
        for src in i_patterns:
            im.update(
                {"source": src},
                {"$set": {"patterns": list(i_patterns[src])}},
                upsert=True
            )
        # Remove obsolete sources
        im.remove({"source": {"$nin": list(i_patterns)}})

    ##
    ## Variable decoders
    ##
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

    def iter_new_events(self, max_chunk=1000):
        """
        Generator iterating unclassified events in the queue
        """
        for e in NewEvent.objects.order_by("seq")[:max_chunk]:
            yield e

    def mark_as_failed(self, event, traceback=None):
        """
        Write error log and mark event as failed
        """
        # Check object still exists
        try:
            event.managed_object
        except ManagedObject.DoesNotExist:
            self.logger.error("Deleting orphaned event %s", str(event.id))
            event.delete()
            return
        if traceback:
            self.logger.error("Failed to process event %s: %s",
                              str(event.id), traceback)
        else:
            self.logger.error("Failed to process event %s", str(event.id))
            # Prepare traceback
            t, v, tb = sys.exc_info()
            now = datetime.datetime.now()
            r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
            r += [str(t), str(v)]
            r += [format_frames(get_traceback_frames(tb))]
            traceback = "\n".join(r)
        event.mark_as_failed(version=self.version, traceback=traceback)

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
            for r in lookup.lookup_rules(event):
                # Try to match rule
                v = r.match(event, vars)
                if v is not None:
                    self.logger.debug("[%s] Matching class for event %s found: %s (Rule: %s)",
                        event.managed_object.name, event.id, r.event_class_name, r.name)
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
                except InterfaceTypeError, why:
                    raise EventProcessingFailed("Cannot decode variable '%s'. Invalid %s: %s", ecv.name, ecv.type, repr(v))
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
        return noc.inv.models.Interface.objects.filter(
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
                        # Signature is already seen, supress
                        event.delete()
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
            event.delete()
            return CR_DELETED
        if rule.is_unknown_syslog:
            # Append codebook
            msg = event.raw_vars.get("message", "")
            cb = self.get_msg_codebook(msg)
            o_id = event.managed_object.id
            if not o_id in self.unclassified_codebook:
                self.unclassified_codebook[o_id] = []
            cbs = [cb] + self.unclassified_codebook[o_id]
            cbs = cbs[:self.unclassified_codebook_depth]
            self.unclassified_codebook[o_id] = cbs
        event_class = rule.event_class
        # Calculate rule variables
        vars = self.eval_rule_variables(event, event_class, vars)
        # Additionally check link events
        disposable = True
        if event_class.link_event and "interface" in vars:
            if_name = event.managed_object.profile.convert_interface_name(vars["interface"])
            iface = self.get_interface(event.managed_object.id, if_name)
            if iface:
                self.logger.debug("Found interface %s:%s",
                                  event.managed_object.name, iface.name)
                action = iface.profile.link_events
            else:
                self.logger.debug("Interface not found %s:%s",
                                  event.managed_object.name, if_name)
                action = self.default_link_action
            if action == "I":
                # Ignore
                if iface:
                    self.logger.info("Event %s has been marked as ignored by interface profile '%s' (%s)", event.id, iface.profile.name, iface.name)
                else:
                    self.logger.info("Event %s has been marked as ignored by default interface profile", event.id)
                event.delete()
                return CR_DELETED
            elif action == "L":
                # Do not dispose
                if iface:
                    self.logger.info("Event %s has been marked as not disposable by interface profile '%s' (%s)", event.id, iface.profile.name, iface.name)
                else:
                    self.logger.info("Event %s has been marked as not disposable by default interface", event.id)
                disposable = False
        # Deduplication
        if self.deduplication_window:
            de = self.find_duplicated_event(event, event_class, vars)
            if de:
                self.logger.debug(
                    "[%s] Event %s duplicates event %s. Discarding",
                    event.managed_object.name, event.id, de.id)
                de.log_message(
                    "Duplicated event %s has been discarded" % event.id
                )
                event.delete()
                return CR_DUPLICATED
        # Suppress repeats
        if event_class.id in self.suppression:
            suppress, name, nearest = self.to_suppress(event, event_class,
                                                       vars)
            if suppress:
                self.logger.debug("[%s] Event %s was suppressed by rule %s",
                    event.managed_object.name, event.id, name)
                # Update suppressing event
                nearest.log_suppression(event.timestamp)
                # Delete suppressed event
                event.delete()
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
            log=log
        )
        a_event.save()
        event.delete()
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
                    self.logger.debug(
                        "[%s] Event dropped by handler",
                        event.managed_object.name
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
                    self.logger.debug(
                        "[%s] Drop event %s (Requested by trigger %s)",
                        event.managed_object.name,
                        event_id, t.name
                    )
                    event.id = event_id  # Restore event id
                    event.delete()
                    return CR_DELETED
        # Finally dispose event to further processing by noc-correlator
        if disposable and rule.to_dispose:
            self.correlator_scheduler.submit_event(event)
            return CR_DISPOSED
        elif rule.is_unknown:
            return CR_UNKNOWN
        else:
            return CR_CLASSIFIED

    def find_duplicated_event(self, event, event_class, vars):
        """
        Returns duplicated event if exists
        """
        t0 = event.timestamp - datetime.timedelta(seconds=self.deduplication_window)
        q = {
            "managed_object": event.managed_object.id,
            "timestamp__gte": t0,
            "timestamp__lte": event.timestamp,
            "event_class": event_class.id
        }
        for v in vars:
            q["vars__%s" % v] = vars[v]
        return ActiveEvent.objects.filter(**q).first()

    def consume_event(self, e):
        """
        Consume single event and return classification status
        """
        try:
            return self.classify_event(e)
        except EventProcessingFailed, why:
            self.mark_as_failed(e, why[0])
            return CR_FAILED
        except:
            self.mark_as_failed(e)
            return CR_FAILED
        finally:
            reset_queries()

    def run(self):
        """
        Main daemon loop
        """
        # @todo: move to configuration
        CHECK_EVERY = 1  # Recheck queue every N seconds
        REPORT_INTERVAL = 1000  # Performance report interval
        OM_UPDATE_INTERVAL = 600
        # Try to classify events which processing failed
        # on previous versions of classifier
        self.retry_failed_events()
        if self.is_distributed:
            self.update_object_map()
        nu = time.time() + OM_UPDATE_INTERVAL
        self.logger.info("Ready to process events")
        st = {
            CR_FAILED: 0, CR_DELETED: 0, CR_SUPPRESSED: 0,
            CR_UNKNOWN: 0, CR_CLASSIFIED: 0, CR_DISPOSED: 0,
            CR_DUPLICATED: 0, CR_UDUPLICATED: 0
        }
        # Enter main loop
        while True:
            n = 0  # Number of events processed
            sn = st.copy()
            t0 = time.time()
            if self.is_distributed and t0 > nu:
                self.update_object_map()
                nu = t0 + OM_UPDATE_INTERVAL
            for e in self.iter_new_events(REPORT_INTERVAL):
                s = self.consume_event(e)
                sn[s] += 1
                n += 1
            if n:
                # Write performance report
                tt = time.time()
                dt = tt - t0
                if dt:
                    perf = n / dt
                else:
                    perf = 0
                s = [
                    "elapsed: %ss" % ("%10.4f" % dt).strip(),
                    "speed: %sev/s" % ("%10.1f" % perf).strip(),
                    "events: %d" % n,
                    "lag: %fs" % total_seconds(datetime.datetime.now() - e.timestamp)
                ]
                s += ["%s: %d" % (CR[i], sn[i]) for i in range(len(CR))]
                s = ", ".join(s)
                self.logger.info("REPORT: %s", s)
            else:
                # No events classified this pass. Sleep
                time.sleep(CHECK_EVERY)

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
