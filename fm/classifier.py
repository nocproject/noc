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
## NOC modules
from noc.lib.daemon import Daemon
from noc.fm.models import EventClassificationRule, NewEvent, FailedEvent, \
                          EventClass, MIB, EventLog,\
                          ActiveEvent, EventTrigger, Enumeration
from noc.sa.models import profile_registry
from noc.lib.version import get_version
from noc.lib.debug import format_frames, get_traceback_frames, error_report
from noc.lib.snmputils import render_tc
from noc.lib.escape import fm_unescape, fm_escape
from noc.sa.interfaces.base import *
from noc.lib.datasource import datasource_registry


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


class Rule(object):
    """
    In-memory rule representation
    """
    
    rx_escape = re.compile(r"\\(.)")
    rx_exact = re.compile(r"^\^[a-zA-Z0-9%: \-_]+\$$")
    
    def __init__(self, classifier, rule):
        self.classifier = classifier
        self.rule = rule
        self.name = rule.name
        self.event_class = rule.event_class
        self.event_class_name = self.event_class.name
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
                    rx_key = re.compile(x.key_re, re.MULTILINE | re.DOTALL)
                except Exception, why:
                    raise InvalidPatternException("Error in '%s': %s" % (x.key_re, why))
            # Process value pattern
            if self.is_exact(x.value_re):
                x_value = self.unescape(x.value_re[1:-1])
            else:
                try:
                    rx_value = re.compile(x.value_re, re.MULTILINE | re.DOTALL)
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
            for k, v in self.vars.items():
                if isinstance(v, basestring):
                    c += ["e_vars[\"%s\"] = \"%s\"" % (k, pyq(v))]
                else:
                    c += ["e_vars[\"%s\"] = eval(self.vars[\"%s\"], {}, e_vars)" % (k, k)]
        if e_vars_used:
            #c += ["return self.fixup(e_vars)"]
            for name in self.fixups:
                r = name.split("__")
                if len(r) == 2:
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
        cc += ["def match(self, vars):"]
        cc += c
        cc += ["rule.match = new.instancemethod(match, rule, rule.__class__)"]
        c = "\n".join(cc)
        code = compile(c, "<string>", "exec")
        exec code in {"rule": self, "new": new,
                      "logging": logging, "fm_unescape": fm_unescape}

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
        """
        return self.classifier.enumerations[name][v.lower()]


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
        Daemon.__init__(self)
        logging.info("Running Classifier version %s" % self.version)

    def load_config(self):
        """
        Load rules from database after loading config
        """
        super(Classifier, self).load_config()
        self.load_enumerations()
        self.load_rules()
        self.load_triggers()

    def load_rules(self):
        """
        Load rules from database
        """
        logging.info("Loading rules")
        n = 0
        profiles = list(profile_registry.classes)
        self.rules = {}
        for p in profiles:
            self.rules[p] = []
        for r in EventClassificationRule.objects.order_by("preference"):
            try:
                rule = Rule(self, r)
            except InvalidPatternException, why:
                logging.error("Failed to load rule '%s': Invalid patterns: %s" % (r.name, why))
                continue
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
        logging.info("%d rules are loaded in the %d profiles" % (n,
                                                            len(self.rules)))
    
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
        return IPPrefixParameter().clean(value)

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
        for e in FailedEvent.objects.filter(version__ne=self.version):
            e.mark_as_new("Reclassification has been requested by noc-classifer")
            logging.debug("Failed event %s has been recovered" % e.id)

    def iter_new_events(self, max_chunk=1000):
        """
        Generator iterating unclassified events in the queue
        """
        for e in NewEvent.objects.order_by("timestamp")[:max_chunk]:
            yield e

    def mark_as_failed(self, event, traceback=None):
        """
        Write error log and mark event as failed
        """
        if traceback:
            logging.error("Failed to process event %s: %s" % (str(event.id), traceback))
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

    def is_oid(self, v):
        """
        Check value is SNMP OID
        """
        return self.rx_oid.match(v) is not None

    def format_snmp_trap_vars(self, event):
        """
        Try to resolve SNMP Trap variables according to MIBs

        :param event: event
        :type event: NewEvent
        :returns: Resolved variables
        :rtype: dict
        """
        r = {}
        for k, v in event.raw_vars.items():
            if not self.is_oid(k):
                # Nothing to resolve
                continue
            v = fm_unescape(v)
            rk, syntax = MIB.get_name_and_syntax(k)
            rv = v
            if syntax:
                # Format value according to syntax
                if syntax["base_type"] == "Enumeration":
                    # Expand enumerated type
                    try:
                        rv = syntax["enum_map"][str(v)]
                    except KeyError:
                        pass
                elif syntax["base_type"] == "Bits":
                    # @todo: Fix ugly hack
                    if v.startswith("="):
                        xv = int(v[1:], 16)
                    else:
                        xv = 0
                        for c in v:
                            xv = (xv << 8) + ord(c)
                    # Decode
                    b_map = syntax.get("enum_map", {})
                    b = []
                    n = 0
                    while xv:
                        if xv & 1:
                            x = str(n)
                            if x in b_map:
                                b = [b_map[x]] + b
                            else:
                                b = ["%X" % (1 << n)]
                        n += 1
                        xv >>= 1
                    rv = "(%s)" % ",".join(b)
                else:
                    # Render according to TC
                    rv = render_tc(v, syntax["base_type"],
                                   syntax.get("display_hint", None))
                    try:
                        unicode(rv, "utf8")
                    except:
                        # Escape invalid UTF8
                        rv = fm_escape(rv)
            else:
                try:
                    unicode(rv, "utf8")
                except:
                    # escape invalid UTF8
                    rv = fm_escape(rv)
            if self.is_oid(v):
                # Resolve OID in value
                rv = MIB.get_name(v)
            if rk != k or rv != v:
                r[rk] = rv
        return r

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
            v = r.match(vars)
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

    def classify_event(self, event):
        """
        Perform event classification.
        Classification steps are:

        1. Format SNMP values accordind to MIB definitions (for SNMP events only)
        2. Find matching classification rule
        3. Calculate rule variables

        :param event: Event to classify
        :type event: NewEvent
        """
        resolved_vars = {
            "profile": event.managed_object.profile_name
        }
        # For SNMP traps format values according to MIB definitions
        if event.source == "SNMP Trap":
            resolved_vars.update(self.format_snmp_trap_vars(event))
        # Find matched event class
        c_vars = event.raw_vars.copy()
        c_vars.update(resolved_vars)
        rule, vars = self.find_matching_rule(event, c_vars)
        if rule is None:
            # Somethin goes wrong. No default rule found. Exit immediately
            logging.error("No default rule found. Exiting")
            os._exit(1)
        if rule.to_drop:
            # Silently drop event if declared by action
            event.delete()
            return
        event_class = rule.event_class
        # Calculate rule variables
        vars = self.eval_rule_variables(event, event_class, vars)
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
                    return
        # Finally dispose event to further processing by noc-correlator
        if rule.to_dispose:
            event.dispose_event()

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
        # Enter main loop
        while True:
            n = 0  # Number of events processed
            sn = 0  # Number of successes
            t0 = time.time()
            for e in self.iter_new_events(REPORT_INTERVAL):
                try:
                    self.classify_event(e)
                    sn += 1
                except EventProcessingFailed, why:
                    self.mark_as_failed(e, why[0])
                except:
                    self.mark_as_failed(e)
                n += 1
            if n:
                # Write performance report
                dt = time.time() - t0
                if dt:
                    perf = n / dt
                else:
                    perf = 0
                logging.info("%d events are classified (success: %d, failed: %d)"
                             "(%10.4f second elapsed. %10.4f events/sec)" % (
                                    n, sn, n - sn, dt, perf))
            else:
                # No events classified this pass. Sleep
                time.sleep(CHECK_EVERY)
