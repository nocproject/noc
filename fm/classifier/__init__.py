# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-classifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import logging
import time
import datetime
import sys
import os
import new
## Django modules
from django.db import reset_queries
## NOC modules
from noc.lib.daemon import Daemon
from noc.fm.models import (EventClassificationRule, NewEvent, FailedEvent,
                           EventClass, MIB, EventLog, CloneClassificationRule,
                           ActiveEvent, EventTrigger, Enumeration)
from noc.inv.models import Interface, SubInterface, InterfaceProfile
from noc.fm.correlator.scheduler import CorrelatorScheduler
import noc.inv.models
from noc.sa.models import profile_registry, ManagedObject
from noc.lib.version import get_version
from noc.lib.debug import format_frames, get_traceback_frames, error_report
from noc.lib.escape import fm_unescape
from noc.sa.interfaces.base import (IPv4Parameter, IPv6Parameter,
                                    IPParameter, IPv4PrefixParameter,
                                    IPv6PrefixParameter, PrefixParameter,
                                    MACAddressParameter, InterfaceTypeError)
from noc.lib.datasource import datasource_registry
from noc.lib.nosql import ObjectId


##
## Exceptions
##
class InvalidPatternException(Exception):
    pass


class EventProcessingFailed(Exception):
    pass
##
## Patterns
##
rx_oid = re.compile(r"^(\d+\.){6,}$")
rx_named_group = re.compile(r"\(\?P<([^>]+)>")


class Trigger(object):
    def __init__(self, t):
        self.name = t.name
        # Condition
        self.condition = compile(t.condition, "<string>", "eval")
        self.time_pattern = t.time_pattern
        self.selector = t.selector
        # Action
        self.notification_group = t.notification_group
        self.template = t.template
        self.pyrule = t.pyrule

    def match(self, event):
        """
        Check event matches trigger condition
        """
        return (eval(self.condition, {}, {"event": event, "re": re}) and
                (self.time_pattern.match(event.timestamp) if self.time_pattern else True) and
                (self.selector.match(event.managed_object) if self.selector else True))
        
    def call(self, event):
        if not self.match(event):
            return
        logging.debug("Calling trigger '%s'" % self.name)
        # Notify if necessary
        if self.notification_group and self.template:
            subject = {}
            body = {}
            for lang in self.notification_group.languages:
                s = event.get_translated_subject(lang)
                b = event.get_translated_body(lang)
                subject[lang] = self.template.render_subject(LANG=lang,
                                                event=event, subject=s, body=b)
                body[lang] = self.template.render_body(LANG=lang,
                                                event=event, subject=s, body=b)
            self.notification_group.notify(subject=subject, body=body)
        # Call pyRule
        if self.pyrule:
            self.pyrule(event=event)


class CloningRule(object):
    class Pattern(object):
        def __init__(self, key_re, value_re):
            self.key_re = key_re
            self.value_re = value_re

        def __unicode__(self):
            return u"%s : %s" % (self.key_re, self.value_re)

    def __init__(self, rule):
        self.re_mode = rule.re != r"^.*$"  # Search by "re"
        self.name = rule.name
        try:
            self.re = re.compile(rule.re)
        except Exception, why:
            raise InvalidPatternException("Error in '%s': %s" % (rule.re, why))
        try:
            self.key_re = re.compile(rule.key_re)
        except Exception, why:
            raise InvalidPatternException("Error in '%s': %s" % (rule.key_re,
                                          why))
        try:
            self.value_re = re.compile(rule.value_re)
        except Exception, why:
            raise InvalidPatternException("Error in '%s': %s" % (rule.value_re,
                                          why))
        try:
            self.rewrite_from = re.compile(rule.rewrite_from)
        except Exception, why:
            raise InvalidPatternException("Error in '%s': %s" % (
                                          rule.rewrite_from, why))
        self.rewrite_to = rule.rewrite_to

    def match(self, rule):
        """
        Check cloning rule matches classification rule
        :rtype: bool
        """
        if self.re_mode:
            c = lambda x: (self.re.search(x.key_re) or
                           self.re.search(x.value_re))
        else:
            c = lambda x: (self.key_re.search(x.key_re) and
                           self.value_re.search(x.value_re))
        return any(x for x in rule.rule.patterns if c(x))

    def rewrite(self, pattern):
        return CloningRule.Pattern(
            self.rewrite_from.sub(self.rewrite_to, pattern.key_re),
            self.rewrite_from.sub(self.rewrite_to, pattern.value_re))


class Rule(object):
    """
    In-memory rule representation
    """
    
    rx_escape = re.compile(r"\\(.)")
    rx_exact = re.compile(r"^\^[a-zA-Z0-9%: \-_]+\$$")
    rx_hex = re.compile(r"(?<!\\)\\x([0-9a-f][0-9a-f])", re.IGNORECASE)
    
    def __init__(self, classifier, rule, clone_rule=None):
        self.classifier = classifier
        self.rule = rule
        self.name = rule.name
        if clone_rule:
            self.name += "(Clone %s)" % clone_rule.name
            if classifier.dump_clone:
                # Dump cloned rule
                logging.debug("Rule '%s' cloned by rule '%s'" % (
                    rule.name, clone_rule.name))
                p0 = [(x.key_re, x.value_re) for x in rule.patterns]
                p1 = [(y.key_re, y.value_re) for y in [
                                clone_rule.rewrite(x) for x in rule.patterns]]
                logging.debug("%s -> %s" % (p0, p1))
        self.event_class = rule.event_class
        self.event_class_name = self.event_class.name
        self.is_unknown = self.event_class_name.startswith("Unknown | ")
        self.datasources = {}  # name -> DS
        self.vars = {}  # name -> value
        # Parse datasources
        for ds in rule.datasources:
            self.datasources[ds.name] = eval(
                    "lambda vars: datasource_registry['%s'](%s)" % (
                        ds.datasource,
                        ", ".join(["%s=vars['%s']" % (k, v)
                                   for k, v in ds.search.items()])),
                    {"datasource_registry": datasource_registry}, {})
        # Parse vars
        for v in rule.vars:
            value = v["value"]
            if value.startswith("="):
                value = compile(value[1:], "<string>", "eval")
            self.vars[v["name"]] = value
        # Parse patterns
        c1 = []
        c2 = {}
        c3 = []
        c4 = []
        self.rxp = {}
        self.fixups = set()
        self.profile = None
        for x in rule.patterns:
            if clone_rule:
                # Rewrite, when necessary
                x = clone_rule.rewrite(x)
            x_key = None
            rx_key = None
            x_value = None
            rx_value = None
            # Store profile
            if x.key_re in ("profile", "^profile$"):
                self.profile = x.value_re
                continue
            # Process key pattern
            if self.is_exact(x.key_re):
                x_key = self.unescape(x.key_re[1:-1])
            else:
                try:
                    rx_key = re.compile(self.unhex_re(x.key_re), re.MULTILINE | re.DOTALL)
                except Exception, why:
                    raise InvalidPatternException("Error in '%s': %s" % (x.key_re, why))
            # Process value pattern
            if self.is_exact(x.value_re):
                x_value = self.unescape(x.value_re[1:-1])
            else:
                try:
                    rx_value = re.compile(self.unhex_re(x.value_re), re.MULTILINE | re.DOTALL)
                except Exception, why:
                    raise InvalidPatternException("Error in '%s': %s" % (x.value_re, why))
            # Save patterns
            if x_key:
                c1 += ["'%s' in vars" % x_key]
                if x_value:
                    c1 += ["vars['%s'] == '%s'" % (x_key, x_value)]
                else:
                    c2[x_key] = self.get_rx(rx_value)
            else:
                if x_value:
                    c3 += [(self.get_rx(rx_key), x_value)]
                else:
                    c4 += [(self.get_rx(rx_key), self.get_rx(rx_value))]
        self.to_drop = self.event_class.action == "D"
        self.to_dispose = len(self.event_class.disposition) > 0
        self.compile(c1, c2, c3, c4)

    def __unicode__(self):
        return self.name
    
    def __repr__(self):
        return "<Rule '%s'>" % self.name
    
    def get_rx(self, rx):
        n = len(self.rxp)
        self.rxp[n] = rx.pattern
        setattr(self, "rx_%d" % n, rx)
        for match in rx_named_group.finditer(rx.pattern):
            name = match.group(1)
            if "__" in name:
                self.fixups.add(name)
        return n

    def unescape(self, pattern):
        return self.rx_escape.sub(lambda m: m.group(1), pattern)

    def unhex_re(self, pattern):
        return self.rx_hex.sub(lambda m: chr(int(m.group(1), 16)), pattern)

    def is_exact(self, pattern):
        return self.rx_exact.match(self.rx_escape.sub("", pattern)) is not None
    
    def compile(self, c1, c2, c3, c4):
        """
        Compile native python rule-matching function
        and install it as .match() instance method
        """
        def pyq(s):
            return s.replace("\\", "\\\\").replace("\"", "\\\"")

        e_vars_used = c2 or c3 or c4
        c = []
        if e_vars_used:
            c += ["e_vars = {}"]
        if c1:
            cc = " and ".join(["(%s)" % x for x in c1])
            c += ["if not (%s):" % cc]
            c += ["    return None"]
        if c2:
            cc = ""
            for k in c2:
                c += ["# %s" % self.rxp[c2[k]]]
                c += ["match = self.rx_%s.search(vars['%s'])" % (c2[k], k)]
                c += ["if not match:"]
                c += ["    return None"]
                c += ["e_vars.update(match.groupdict())"]
        if c3:
            for rx, v in c3:
                c += ["found = False"]
                c += ["for k in vars:"]
                c += ["    # %s" % self.rxp[rx]]
                c += ["    match = self.rx_%s.search(k)" % rx]
                c += ["    if match:"]
                c += ["        if vars[k] == '%s':" % v]
                c += ["            e_vars.update(match.groupdict())"]
                c += ["            found = True"]
                c += ["            break"]
                c += ["        else:"]
                c += ["            return None"]
                c += ["if not found:"]
                c += ["    return None"]
        if c4:
            for rxk, rxv in c4:
                c += ["found = False"]
                c += ["for k in vars:"]
                c += ["    # %s" % self.rxp[rxk]]
                c += ["    match_k = self.rx_%s.search(k)" % rxk]
                c += ["    if match_k:"]
                c += ["        # %s" % self.rxp[rxv]]
                c += ["        match_v = self.rx_%s.search(vars[k])" % rxv]
                c += ["        if match_v:"]
                c += ["            e_vars.update(match_k.groupdict())"]
                c += ["            e_vars.update(match_v.groupdict())"]
                c += ["            found = True"]
                c += ["            break"]
                c += ["        else:"]
                c += ["            return None"]
                c += ["if not found:"]
                c += ["    return None"]
        # Vars binding
        if self.vars:
            has_expressions = any(v for v in self.vars.values()
                                  if not isinstance(v, basestring))
            if has_expressions:
                # Callculate vars context
                c += ["var_context = {'event': event}"]
                c += ["var_context.update(e_vars)"]
            for k, v in self.vars.items():
                if isinstance(v, basestring):
                    c += ["e_vars[\"%s\"] = \"%s\"" % (k, pyq(v))]
                else:
                    c += ["e_vars[\"%s\"] = eval(self.vars[\"%s\"], {}, var_context)" % (k, k)]
        if e_vars_used:
            #c += ["return self.fixup(e_vars)"]
            for name in self.fixups:
                r = name.split("__")
                if len(r) == 2:
                    if r[1] in ("ifindex",):
                        # call fixup with managed object
                        c += ["e_vars[\"%s\"] = self.fixup_%s(event.managed_object, fm_unescape(e_vars[\"%s\"]))" % (r[0], r[1], name)]
                    else:
                        c += ["e_vars[\"%s\"] = self.fixup_%s(fm_unescape(e_vars[\"%s\"]))" % (r[0], r[1], name)]
                else:
                    c += ["args = [%s, fm_unescape(e_vars[\"%s\"])]" % (", ".join(["\"%s\"" % x for x in r[2:]]), name)]
                    c += ["e_vars[\"%s\"] = self.fixup_%s(*args)" % (r[0], r[1])]
                c += ["del e_vars[\"%s\"]" % name]
            c += ["return e_vars"]
        else:
            c += ["return {}"]
        c = ["    " + l for l in c]
        
        cc = ["# %s" % self.name]
        cc += ["def match(self, event, vars):"]
        cc += c
        cc += ["rule.match = new.instancemethod(match, rule, rule.__class__)"]
        c = "\n".join(cc)
        code = compile(c, "<string>", "exec")
        exec code in {"rule": self, "new": new,
                      "logging": logging, "fm_unescape": fm_unescape}

    def clone(self, rules):
        """
        Factory returning clone rules
        """
        pass

    def fixup_int_to_ip(self, v):
        v = long(v)
        return "%d.%d.%d.%d" % (
            v & 0xFF000000 >> 24,
            v & 0x00FF0000 >> 16,
            v & 0x0000FF00 >> 8,
            v & 0x000000FF)

    def fixup_bin_to_ip(self, v):
        """
        Fix 4-octet binary ip to dotted representation
        """
        if len(v) != 4:
            return v
        return "%d.%d.%d.%d" % (ord(v[0]), ord(v[1]), ord(v[2]), ord(v[3]))

    def fixup_bin_to_mac(self, v):
        """
        Fix 6-octet binary to standard MAC address representation
        """
        if len(v) != 6:
            return v
        return ":".join(["%02X" % ord(x) for x in v])

    def fixup_oid_to_str(self, v):
        """
        Fix N.c1. .. .cN into "c1..cN" string
        """
        x = [int(c) for c in v.split(".")]
        return "".join([chr(c) for c in x[1:x[0] + 1]])

    def fixup_enum(self, name, v):
        """
        Resolve v via enumeration name
        @todo: not used?
        """
        return self.classifier.enumerations[name][v.lower()]

    def fixup_ifindex(self, managed_object, v):
        """
        Resolve ifindex to interface name
        """
        ifindex = int(v)
        # Try to resolve interface
        i = Interface.objects.filter(
            managed_object=managed_object.id, ifindex=ifindex).first()
        if i:
            return i.name
        # Try to resolve subinterface
        si = SubInterface.objects.filter(
            managed_object=managed_object.id, ifindex=ifindex).first()
        if si:
            return si.name
        return v

CR_FAILED = 0
CR_DELETED = 1
CR_SUPPRESSED = 2
CR_UNKNOWN = 3
CR_CLASSIFIED = 4
CR_DISPOSED = 5
CR_DUPLICATED = 6
CR = ["failed", "deleted", "suppressed",
      "unknown", "classified", "disposed", "duplicated"]


class Classifier(Daemon):
    """
    noc-classifier daemon
    """
    daemon_name = "noc-classifier"

    # SNMP OID pattern
    rx_oid = re.compile(r"^(\d+\.){6,}")

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
        # Default link event action, when interface is not in inventory
        self.default_link_action = None
        Daemon.__init__(self)
        logging.info("Running Classifier version %s" % self.version)
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
        self.load_enumerations()
        self.load_rules()
        self.load_triggers()
        self.load_suppression()
        self.load_link_action()

    def load_rules(self):
        """
        Load rules from database
        """
        logging.info("Loading rules")
        n = 0
        cn = 0
        profiles = list(profile_registry.classes)
        self.rules = {}
        # Initialize profiles
        for p in profiles:
            self.rules[p] = []
        # Load cloning rules
        cloning_rules = []
        for cr in CloneClassificationRule.objects.all():
            try:
                cloning_rules += [CloningRule(cr)]
            except InvalidPatternException, why:
                logging.error("Failed to load cloning rule '%s': Invalid pattern: %s" % (cr.name, why))
                continue
        logging.info("%d cloning rules found" % len(cloning_rules))
        # Initialize rules
        for r in EventClassificationRule.objects.order_by("preference"):
            try:
                rule = Rule(self, r)
            except InvalidPatternException, why:
                logging.error("Failed to load rule '%s': Invalid patterns: %s" % (r.name, why))
                continue
            # Apply cloning rules
            rs = [rule]
            for cr in cloning_rules:
                if cr.match(rule):
                    try:
                        rs += [Rule(self, r, cr)]
                        cn += 1
                    except InvalidPatternException, why:
                        logging.error("Failed to clone rule '%s': Invalid patterns: %s" % (r.name, why))
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
                        self.rules[p] += [rule]
                n += 1
        if cn:
            logging.info("%d rules are cloned" % cn)
        logging.info("%d rules are loaded in the %d profiles" % (
            n, len(self.rules)))
    
    def load_triggers(self):
        logging.info("Loading triggers")
        self.triggers = {}
        n = 0
        cn = 0
        ec = [(c.name, c.id) for c in EventClass.objects.all()]
        for t in EventTrigger.objects.filter(is_enabled=True):
            logging.debug("Trigger '%s' for classes:" % t.name)
            for c_name, c_id in ec:
                if re.search(t.event_class_re, c_name, re.IGNORECASE):
                    try:
                        self.triggers[c_id] += [Trigger(t)]
                    except KeyError:
                        self.triggers[c_id] = [Trigger(t)]
                    cn += 1
                    logging.debug("    %s" % c_name)
            n += 1
        logging.info("%d triggers has been loaded to %d classes" % (n, cn))

    def load_enumerations(self):
        logging.info("Loading enumerations")
        n = 0
        self.enumerations = {}
        for e in Enumeration.objects.all():
            r = {}
            for k, v in e.values.items():
                for vv in v:
                    r[vv.lower()] = k
            self.enumerations[e.name] = r
            n += 1
        logging.info("%d enumerations loaded" % n)

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

        logging.info("Loading suppression rules")
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
        logging.info("Suppression rules are loaded")

    def load_link_action(self):
        self.default_link_action = None
        profile_name = self.config.get(
            "classifier", "default_interface_profile").strip()
        if profile_name:
            p = InterfaceProfile.objects.filter(name=profile_name).first()
            if p:
                logging.info("Setting default link event action to %r" % p.link_events)
                self.default_link_action = p.link_events

    ##
    ## Variable decoders
    ##
    def decode_str(self, event, value):
        return value

    def decode_int(self, event, value):
        return int(value)

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
        logging.info("Recovering failed events")
        wm = datetime.datetime.now() - datetime.timedelta(seconds=86400)  # @todo: use config
        dc = FailedEvent.objects.filter(timestamp__lt=wm).count()
        if dc > 0:
            logging.info("%d failed events are deprecated and removed" % dc)
            FailedEvent.objects.filter(timestamp__lt=wm).delete()
        for e in FailedEvent.objects.filter(version__ne=self.version):
            e.mark_as_new("Reclassification has been requested by noc-classifer")
            logging.debug("Failed event %s has been recovered" % e.id)

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
            logging.error("Deleting orphaned event %s" % str(event.id))
            event.delete()
            return
        if traceback:
            logging.error("Failed to process event %s: %s" % (str(event.id),
                                                              traceback))
        else:
            logging.error("Failed to process event %s" % str(event.id))
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
        for r in self.rules[event.managed_object.profile_name]:
            # Try to match rule
            v = r.match(event, vars)
            if v is not None:
                logging.debug("Matching class for event %s found: %s (Rule: %s)" % (
                    event.id, r.event_class_name, r.name))
                return r, v
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
        # For SNMP traps format values according to MIB definitions
        if event.source == "SNMP Trap":
            resolved_vars.update(MIB.resolve_vars(event.raw_vars))
        # Find matched event class
        c_vars = event.raw_vars.copy()
        c_vars.update(dict([(k, fm_unescape(v)) for k, v in resolved_vars.items()]))
        rule, vars = self.find_matching_rule(event, c_vars)
        if rule is None:
            # Something goes wrong.
            # No default rule found. Exit immediately
            logging.error("No default rule found. Exiting")
            os._exit(1)
        if rule.to_drop:
            # Silently drop event if declared by action
            event.delete()
            return CR_DELETED
        event_class = rule.event_class
        # Calculate rule variables
        vars = self.eval_rule_variables(event, event_class, vars)
        # Additionally check link events
        disposable = True
        if event_class.link_event and "interface" in vars:
            iface = noc.inv.models.Interface.objects.filter(
                managed_object=event.managed_object.id,
                name=event.managed_object.profile.convert_interface_name(vars["interface"])
            ).first()
            if iface:
                action = iface.profile.link_events
            else:
                action = self.default_link_action
            if action == "I":
                # Ignore
                if iface:
                    msg = "Event %s has been marked as ignored by interface profile '%s' (%s)" % (event.id, iface.profile.name, iface.name)
                else:
                    msg = "Event %s has been marked as ignored by default interface profile" % event.id
                logging.info(msg)
                event.delete()
                return CR_DELETED
            elif action == "L":
                # Do not dispose
                if iface:
                    msg = "Event %s has been marked as not disposable by interface profile '%s' (%s)" % (event.id, iface.profile.name, iface.name)
                else:
                    msg = "Event %s has been marked as not disposable by default interface" % event.id
                logging.info(msg)
                disposable = False
        # Deduplication
        if self.deduplication_window:
            de = self.find_duplicated_event(event, event_class, vars)
            if de:
                logging.debug(
                    "Event %s duplicates event %s. Discarding",
                    event.id, de.id)
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
                logging.debug("Event %s was suppressed by rule %s" % (
                    event.id, name))
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
                    logging.debug("Drop event %s (Requested by trigger %s)" % (
                        event_id, t.name))
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

    def run(self):
        """
        Main daemon loop
        """
        # @todo: move to configuration
        CHECK_EVERY = 3  # Recheck queue every N seconds
        REPORT_INTERVAL = 1000  # Performance report interval
        # Try to classify events which processing failed
        # on previous versions of classifier
        self.retry_failed_events()
        logging.info("Ready to process events")
        st = {
            CR_FAILED: 0, CR_DELETED: 0, CR_SUPPRESSED: 0,
            CR_UNKNOWN: 0, CR_CLASSIFIED: 0, CR_DISPOSED: 0,
            CR_DUPLICATED:0
        }
        # Enter main loop
        while True:
            n = 0  # Number of events processed
            sn = st.copy()
            t0 = time.time()
            for e in self.iter_new_events(REPORT_INTERVAL):
                try:
                    s = self.classify_event(e)
                    sn[s] += 1
                except EventProcessingFailed, why:
                    self.mark_as_failed(e, why[0])
                    sn[CR_FAILED] += 1
                except:
                    self.mark_as_failed(e)
                    sn[CR_FAILED] += 1
                n += 1
                reset_queries()
            if n:
                # Write performance report
                dt = time.time() - t0
                if dt:
                    perf = n / dt
                else:
                    perf = 0
                s = [
                    "elapsed: %ss" % ("%10.4f" % dt).strip(),
                    "speed: %sev/s" % ("%10.1f" % perf).strip(),
                    "events: %d" % n
                    ]
                s += ["%s: %d" % (CR[i], sn[i]) for i in range(len(CR))]
                s = ", ".join(s)
                logging.info("REPORT: %s" % s)
            else:
                # No events classified this pass. Sleep
                time.sleep(CHECK_EVERY)
