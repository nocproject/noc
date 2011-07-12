# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-correlator daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import sys
import datetime
import time
import logging
import hashlib
import re
## NOC modules
from noc.lib.daemon import Daemon
from noc.fm.models import EventDispositionQueue, ActiveEvent, EventClass,\
                          ActiveAlarm, AlarmLog
from noc.main.models import PyRule, PrefixTable, PrefixTablePrefix
from noc.lib.version import get_version
from noc.lib.debug import format_frames, get_traceback_frames


class Rule(object):
    def __init__(self, ec, dr):
        self.name = dr.name
        self.event_class = ec
        self.u_name = "%s: %s" % (self.event_class.name, self.name)
        self.condition = compile(dr.condition, "<string>", "eval")
        self.action = dr.action
        self.pyrule = dr.action == "pyrule" and dr.pyrule and PyRule.objects.get(name=dr.pyrule)
        self.alarm_class = dr.alarm_class
        self.stop_disposition = dr.stop_disposition
        self.var_mapping = {}
        self.discriminator = []
        if self.alarm_class:
            self.severity = self.alarm_class.default_severity.severity
            self.unique = self.alarm_class.is_unique
            a_vars = set([v.name for v in self.alarm_class.vars])
            e_vars = set([v.name for v in self.event_class.vars])
            for v in a_vars.intersection(e_vars):
                self.var_mapping[v] = v
            if dr.var_mapping:
                self.var_mapping.update(dr.var_mapping)
            self.discriminator = self.alarm_class.discriminator
            self.combo_condition = dr.combo_condition
            self.combo_window = dr.combo_window
            self.combo_event_classes = [c.id for c in dr.combo_event_classes]

    def get_vars(self, e):
        """
        Get alarm variables from event.

        :param e: ActiveEvent
        :returns: tuple of (discriminator, vars)
        """
        if self.var_mapping:
            vars = {}
            for k, v in self.var_mapping.items():
                vars[v] = e.vars[k]
            ds = [vars[n] for n in self.discriminator]
            discriminator = hashlib.sha1("\x00".join(ds)).hexdigest()
            return discriminator, vars
        else:
            return hashlib.sha1("").hexdigest(), None


class Correlator(Daemon):
    daemon_name = "noc-correlator"

    def __init__(self):
        self.version = get_version()
        self.rules = {}  # event_class -> [Rule]
        self.back_rules = {}  # event_class -> [Rule]
        Daemon.__init__(self)
        logging.info("Running noc-correlator")
        # Tables
        self.NOC_ACTIVATORS = self.get_activators()  # NOC::Activators prefix table

    def load_config(self):
        """
        Load rules from database just after loading config
        """
        super(Correlator, self).load_config()
        self.load_rules()

    def load_rules(self):
        """
        Load rules from database
        """
        logging.debug("Loading rules")
        self.rules = {}
        self.back_rules = {}
        nr = 0
        nbr = 0
        for c in EventClass.objects.all():
            if c.disposition:
                r = []
                for dr in c.disposition:
                    rule = Rule(c, dr)
                    r += [rule]
                    nr += 1
                    if dr.combo_condition != "none" and dr.combo_window:
                        for cc in combo_event_classes:
                            try:
                                self.back_rules[cc.id] += [dr]
                            except KeyError:
                                self.back_rules[cc.id] = [dr]
                            nbr += 1
                self.rules[c.id] = r
        logging.debug("%d rules are loaded. %d combos" % (nr, nbr))

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

    def iter_new_events(self, max_chunk=100):
        """
        Generator returning ActiveEvents to be disposed
        """
        for de in EventDispositionQueue.objects.order_by("timestamp")[:max_chunk]:
            e = ActiveEvent.objects.filter(id=de.event_id).first()
            de.delete()
            yield e

    def raise_alarm(self, r, e):
        discriminator, vars = r.get_vars(e)
        if r.unique:
            assert discriminator is not None
            a = ActiveAlarm.objects.filter(managed_object=e.managed_object.id,
                                           discriminator=discriminator).first()
            if a:
                # Active alarm found, refresh
                logging.debug("%s: Contirbuting event %s(%s) to active alarm %s(%s)" % (
                    r.u_name, str(e.id), e.event_class.name,
                    str(a.id), a.alarm_class.name))
                a.contribute_event(e)
                a.log_message("Event #%s(%s) has been contributed by rule '%s'" % (
                    str(e.id), e.event_class.name, r.u_name))
                return
        # Create new alarm
        a = ActiveAlarm(timestamp=e.timestamp, last_update=e.timestamp,
                        managed_object=e.managed_object,
                        alarm_class=r.alarm_class,
                        severity=r.severity, vars=vars,
                        discriminator=discriminator,
                        events=[e],
                        log=[
                            AlarmLog(timestamp=datetime.datetime.now(),
                                     from_status="A",
                                     to_status="A",
                                     message="Alarm risen from event %s(%s) by rule '%s'" % (
                                        str(e.id), str(e.event_class.name),
                                        r.u_name
                                        ))
                            ])
        a.save()
        logging.debug("%s: Event %s(%s) raises alarm %s(%s)" % (
            r.u_name, str(e.id), e.event_class.name,
            str(a.id), r.alarm_class.name))

    def clear_alarm(self, r, e):
        if r.unique:
            discriminator, vars = r.get_vars(e)
            assert discriminator is not None
            a = ActiveAlarm.objects.filter(managed_object=e.managed_object.id,
                                           discriminator=discriminator).first()
            if a:
                logging.debug("%s: Event %s(%s) clears alarm %s(%s)" % (
                    r.u_name, str(e.id), e.event_class.name,
                    str(a.id), a.alarm_class.name))
                a.clear_alarm("Cleared by disposition rule '%s'" % r.u_name)

    def get_delayed_event(self, r, e):
        """
        Check wrether all delayed conditions are met

        :param r: Delayed rule
        :param e: Event which can trigger delayed rule
        """
        discriminator, vars = r.get_vars(e)
        ws = e.timestamp - datetime.timedelta(seconds=r.combo_window)
        de = ActiveEvent.objects.filter(
                managed_object=e.managed_object.id,
                event_class=r.event_class,
                discriminator=discriminator,
                timestamp__gte=ws
                ).first()
        if not de:
            # No starting event
            return None
        # Probable starting event found, get all interesting following event
        # classes
        fe = [ee.event_class.id
              for ee in ActiveEvent.objects.filter(
                managed_object=e.managed_object.id,
                event_class__in=r.combo_event_classes,
                discriminator=discriminator,
                timestamp__gte=ws).order_by("timestamp")]
        if r.combo_condition == "sequence":
            # Exact match
            if fe == self.combo_event_classes:
                return de
        elif r.combo_condition == "all":
            # All present
            if not any([c for c in r.combo_event_classes if c not in fe]):
                return de
        elif r.combo_condition == "any":
            # Any found
            if fe:
                return de
        return None

    def dispose_event(self, e):
        """
        Dispose event according to disposition rule
        """
        drc = self.rules.get(e.event_class.id)
        if not drc:
            return
        # Apply disposition rules
        env = {
            "event": e,
            "NOC_ACTIVATORS": self.NOC_ACTIVATORS,
            "re": re
        }
        for r in drc:
            if eval(r.condition, {}, env):
                # Process action
                if r.action == "drop":
                    event.delete()
                    return
                elif r.action == "ignore":
                    return
                elif r.action == "raise" and r.combo_condition == "none":
                    self.raise_alarm(r, e)
                elif r.action == "clear" and r.combo_condition == "none":
                    self.clear_alarm(r, e)
                if r.action in ("raise", "clear"):
                    # Write discriminator if can trigger delayed event
                    if r.unique and r.event_class.id in self.back_rules:
                        discriminator, vars = r.get_vars(e)
                        e.discriminator = discriminator
                        e.save()
                    # Process delayed combo conditions
                    if e.event_class.id in self.back_rules:
                        for br in self.back_rules[e.event_class.id]:
                            de = self.get_delayed_event(br, e)
                            if de:
                                if br.action == "raise":
                                    self.raise_alarm(br, de)
                                elif br.action == "clear":
                                    self.clear_alarm(br, de)
                if r.stop_disposition:
                    break

    def get_activators(self):
        """
        Get SELF_ADDRESSES instance, or create
        and populate with activator addresses
        and local interface addresses
        """
        try:
            return PrefixTable.objects.get(name="NOC::Activators")
        except PrefixTable.DoesNotExist:
            pass
        # Get prefixes
        prefixes = ["127.0.0.1/32"]
        # Save prefixes
        t = PrefixTable(name="NOC::Activators",
                        description="NOC's activators IP addresses")
        t.save()
        for p in prefixes:
            PrefixTablePrefix(table=t, prefix=p).save()
        return t

    def run(self):
        """
        Main daemon loop
        """
        CHECK_EVERY = 3  # Recheck queue every N seconds
        REPORT_INTERVAL = 100
        while True:
            n = 0
            sn = 0
            t0 = time.time()
            for e in self.iter_new_events(REPORT_INTERVAL):
                try:
                    self.dispose_event(e)
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
                logging.info("%d events are disposed (success: %d, failed: %d)"
                             "(%10.4f second elapsed. %10.4f events/sec)" % (
                                    n, sn, n - sn, dt, perf))
            else:
                # No events classified this pass. Sleep
                time.sleep(CHECK_EVERY)
