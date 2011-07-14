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
## NOC modules
from noc.lib.daemon import Daemon
from noc.fm.models import EventClassificationRule, NewEvent, FailedEvent, \
                          EventClass, MIB, EventLog,\
                          ActiveEvent
from noc.sa.models import profile_registry
from noc.lib.version import get_version
from noc.lib.debug import format_frames, get_traceback_frames
from noc.lib.snmputils import render_tc
from noc.lib.escape import fm_unescape, fm_escape
from noc.sa.interfaces.base import *

##
## Patterns
##
rx_oid = re.compile(r"^(\d+\.){6,}$")


class Rule(object):
    """
    In-memory rule representation
    """
    def __init__(self, rule):
        self.rule = rule
        self.name = rule.name
        self.event_class = rule.event_class
        self.event_class_name = self.event_class.name
        self.patterns = [(re.compile(x.key_re, re.MULTILINE | re.DOTALL),
                          re.compile(x.value_re, re.MULTILINE | re.DOTALL))
                         for x in rule.patterns]
        self.to_drop = self.event_class.action == "D"
        self.to_dispose = len(self.event_class.disposition) > 0

    def __unicode__(self):
        return self.name

    def match(self, vars):
        """
        Try to match variables agains a rule.
        Return extracted variables or None

        :param vars: New and resolved variables
        :type vars: dict
        :returns: Extracted vars or None
        :rtype: dict or None
        """
        e_vars = {}
        for kp, vp in self.patterns:
            found = False
            for k in vars:
                # Try to match key
                k_match = kp.search(k)
                if k_match is None:
                    continue
                v = vars[k]
                v_match = vp.search(v)
                if v_match is None:
                    continue  # ??? return None
                # Matched line found
                found = True
                # Append extracted variables
                e_vars.update(k_match.groupdict())
                e_vars.update(v_match.groupdict())
                break
            if not found:
                # No matched lines found
                return None
        return e_vars


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
        self.templates = {}  # event_class_id -> (body_template,subject_template)
        self.post_process = {}  # event_class_id -> [rule1, ..., ruleN]
        Daemon.__init__(self)
        logging.info("Running Classifier version %s" % self.version)

    def load_config(self):
        """
        Load rules from database after loading config
        """
        super(Classifier, self).load_config()
        self.load_rules()

    def load_rules(self):
        """
        Load rules from database
        """
        def find_profile(rule):
            for l, r in rule.patterns:
                if l.pattern in ("profile", "^profile$"):
                    return r.pattern
            return None

        logging.info("Loading rules")
        n = 0
        profiles = list(profile_registry.classes)
        self.rules = {}
        for p in profiles:
            self.rules[p] = []
        for r in EventClassificationRule.objects.order_by("preference"):
            rule = Rule(r)
            # Find profile restriction
            p = find_profile(rule)
            if p:
                profile_re = p
            else:
                profile_re = r"^.*$"
            rx = re.compile(profile_re)
            for p in profiles:
                if rx.search(p):
                    self.rules[p] += [rule]
            n += 1
        logging.info("%d rules are loaded into %d chains" % (n, len(self.rules)))
        for p in sorted(self.rules):
            logging.debug("%s (%d rules):" % (p, len(self.rules[p])))
            for r in self.rules[p]:
                logging.debug("    %s" % r.name)

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

    def mark_as_failed(self, event):
        """
        Write error log and mark event as failed
        """
        logging.error("Failed to process event %s" % str(event.id))
        # Prepare traceback
        t, v, tb = sys.exc_info()
        now = datetime.datetime.now()
        r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
        r += [str(t), str(v)]
        r += [format_frames(get_traceback_frames(tb))]
        r = "\n".join(r)
        event.mark_as_failed(version=self.version, traceback=r)

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
                else:
                    # Render according to TC
                    rv = render_tc(v, syntax["base_type"],
                                   syntax.get("display_hint", None))
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
                v = decoder(event, v)
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
