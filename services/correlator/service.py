#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-correlator daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import datetime
import logging
import re
from collections import defaultdict
## NOC modules
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler
from rule import Rule
from rcacondition import RCACondition
from trigger import Trigger
from joblauncher import JobLauncher
from noc.fm.models import ActiveEvent, EventClass,\
                          ActiveAlarm, AlarmLog, AlarmTrigger, AlarmClass
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.lib.version import get_version
from noc.lib.debug import format_frames, get_traceback_frames, error_report
from noc.lib.solutions import get_alarm_class_handlers, get_alarm_jobs
import utils


class CorrelatorService(Service):
    name = "correlator"

    def __init__(self):
        super(CorrelatorService, self).__init__()
        self.version = get_version()
        self.rules = {}  # event_class -> [Rule]
        self.back_rules = {}  # event_class -> [Rule]
        self.triggers = {}  # alarm_class -> [Trigger1, .. , TriggerN]
        self.rca_forward = {}  # alarm_class -> [RCA condition, ..., RCA condititon]
        self.rca_reverse = defaultdict(set)  # alarm_class -> set([alarm_class])
        self.alarm_jobs = {}  # alarm_class -> [JobLauncher, ..]
        self.handlers = {}  # alamr class id -> [<handler>]
        self.scheduler = None

    def on_activate(self):
        self.scheduler = Scheduler(
            self.name,
            reset_running=True,
            ioloop=self.ioloop
        )
        self.scheduler.correlator = self
        ActiveAlarm.enable_caching(600)
        self.scheduler.run()

    def load_config(self):
        """
        Load rules from database just after loading config
        """
        super(CorrelatorService, self).load_config()
        self.load_rules()
        self.load_triggers()
        self.load_rca_rules()
        self.load_alarm_jobs()
        self.load_handlers()

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
                        for cc in dr.combo_event_classes:
                            try:
                                self.back_rules[cc.id] += [dr]
                            except KeyError:
                                self.back_rules[cc.id] = [dr]
                            nbr += 1
                self.rules[c.id] = r
        logging.debug("%d rules are loaded. %d combos" % (nr, nbr))

    def load_triggers(self):
        logging.info("Loading triggers")
        self.triggers = {}
        n = 0
        cn = 0
        ec = [(c.name, c.id) for c in AlarmClass.objects.all()]
        for t in AlarmTrigger.objects.filter(is_enabled=True):
            logging.debug("Trigger '%s' for classes:" % t.name)
            for c_name, c_id in ec:
                if re.search(t.alarm_class_re, c_name, re.IGNORECASE):
                    try:
                        self.triggers[c_id] += [Trigger(t)]
                    except KeyError:
                        self.triggers[c_id] = [Trigger(t)]
                    cn += 1
                    logging.debug("    %s" % c_name)
            n += 1
        logging.info("%d triggers has been loaded to %d classes" % (n, cn))

    def load_rca_rules(self):
        """
        Load root cause analisys rules
        """
        logging.debug("Loading RCA Rules")
        n = 0
        self.rca_forward = {}
        self.rca_reverse = {}
        for a in AlarmClass.objects.filter(root_cause__0__exists=True):
            if not a.root_cause:
                continue
            self.rca_forward[a.id] = []
            for c in a.root_cause:
                rc = RCACondition(a, c)
                self.rca_forward[a.id] += [rc]
                if rc.root.id not in self.rca_reverse:
                    self.rca_reverse[rc.root.id] = []
                self.rca_reverse[rc.root.id] += [rc]
                n += 1
        logging.debug("%d RCA Rules have been loaded" % n)

    def load_alarm_jobs(self):
        """
        Load alarm jobs
        :return:
        """
        logging.info("Loading alarm jobs")
        n = 0
        self.alarm_jobs = {}  # class id ->
        for ac in AlarmClass.objects.all():
            continue  # @todo: Port jobs properly
            jobs = get_alarm_jobs(ac)
            if not jobs:
                continue
            logging.debug("    <%s>: %s", ac.name, ", ".join(j.job for j in jobs))
            self.alarm_jobs[ac.id] = [
                JobLauncher(self.scheduler, j.job, j.interval, j.vars)
                for j in jobs]
            n += len(jobs)
        logging.debug("%d alarm jobs have been loaded" % n)

    def load_handlers(self):
        logging.info("Loading handlers")
        self.handlers = {}
        for ac in AlarmClass.objects.filter():
            handlers = get_alarm_class_handlers(ac)
            if not handlers:
                continue
            logging.debug("    <%s>: %s", ac.name, ", ".join(handlers))
            hl = []
            for h in ac.handlers:
                # Resolve handler
                hh = self.resolve_handler(h)
                if hh:
                    hl += [hh]
            if hl:
                self.handlers[ac.id] = hl
        logging.info("Handlers are loaded")

    @classmethod
    def resolve_handler(cls, h):
        mn, s = h.rsplit(".", 1)
        try:
            m = __import__(mn, {}, {}, s)
        except ImportError:
            logging.error("Failed to load handler '%s'. Ignoring" % h)
            return None
        try:
            return getattr(m, s)
        except AttributeError:
            logging.error("Failed to load handler '%s'. Ignoring" % h)
            return None

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

    def set_root_cause(self, a):
        """
        Search for root cause and set, if found
        :returns: Boolean. True, if root cause set
        """
        for rc in self.rca_forward[a.alarm_class.id]:
            # Check condition
            if not rc.check_condition(a):
                continue
            # Check match condition
            q = rc.get_match_condition(a)
            root = ActiveAlarm.objects.filter(**q).first()
            if root:
                # Root cause found
                logging.debug("%s is root cause for %s (Rule: %s)",
                    root.id, a.id, rc.name)
                a.set_root(root)
                return True
        return False

    def set_reverse_root_cause(self, a):
        """
        Set *a* as root cause for existing events
        :param a:
        :return:
        """
        found = False
        for rc in self.rca_reverse[a.alarm_class.id]:
            # Check reverse match condition
            q = rc.get_reverse_match_condition(a)
            for ca in ActiveAlarm.objects.filter(**q):
                # Check condition
                if not rc.check_condition(ca):
                    continue
                # Try to set root cause
                q = rc.get_match_condition(ca)
                q["id"] = a.id
                rr = ActiveAlarm.objects.filter(**q).first()
                if rr:
                    # Reverse root cause found
                    logging.debug(
                        "%s is root cause for %s (Reverse rule: %s)",
                        a.id, ca.id, rc.name
                    )
                    ca.set_root(a)
                    found = True
        return found

    def raise_alarm(self, r, e):
        managed_object = self.eval_expression(r.managed_object, event=e)
        if not managed_object:
            logging.debug("Empty managed object, ignoring")
            return
        if e.managed_object.id != managed_object.id:
            logging.debug("Changing managed object to %s",
                          managed_object.name)
        discriminator, vars = r.get_vars(e)
        if r.unique:
            assert discriminator is not None
            # @todo: unneeded SQL lookup here
            a = ActiveAlarm.objects.filter(
                managed_object=managed_object.id,
                discriminator=discriminator).first()
            if not a:
                # Try to reopen alarm
                a = ArchivedAlarm.objects.filter(
                    managed_object=managed_object.id,
                    discriminator=discriminator,
                    control_time__gte=e.timestamp
                ).first()
                if a:
                    # Reopen alarm
                    logging.debug("%s: Event %s(%s) reopens alarm %s(%s)" % (
                        r.u_name, str(e.id), e.event_class.name,
                        str(a.id), a.alarm_class.name))
                    a = a.reopen("Reopened by disposition rule '%s'" % r.u_name)
            if a:
                # Active alarm found, refresh
                logging.debug("%s: Contributing event %s(%s) to active alarm %s(%s)" % (
                    r.u_name, str(e.id), e.event_class.name,
                    str(a.id), a.alarm_class.name))
                a.contribute_event(e)
                return
        # Create new alarm
        a = ActiveAlarm(
            timestamp=e.timestamp,
            last_update=e.timestamp,
            managed_object=managed_object.id,
            alarm_class=r.alarm_class,
            severity=r.severity,
            vars=vars,
            discriminator=discriminator,
            log=[
                AlarmLog(
                    timestamp=datetime.datetime.now(),
                    from_status="A",
                    to_status="A",
                    message="Alarm risen from event %s(%s) by rule '%s'" % (
                        str(e.id), str(e.event_class.name), r.u_name)
                )
            ]
        )
        a.save()
        a.contribute_event(e, open=True)
        logging.debug("%s: Event %s (%s) raises alarm %s (%s): %r",
                      r.u_name, str(e.id), e.event_class.name,
                      str(a.id), r.alarm_class.name, a.vars)
        # RCA
        if a.alarm_class.id in self.rca_forward:
            # Check alarm is a consequence of existing one
            self.set_root_cause(a)
        if a.alarm_class.id in self.rca_reverse:
            # Check alarm is the root cause for existing ones
            self.set_reverse_root_cause(a)
        # Call handlers
        if a.alarm_class.id in self.handlers:
            for h in self.handlers[a.alarm_class.id]:
                try:
                    h(a)
                except:
                    error_report()
        # Call triggers if necessary
        if r.alarm_class.id in self.triggers:
            for t in self.triggers[r.alarm_class.id]:
                try:
                    t.call(a)
                except:
                    error_report()
        #
        if not a.severity:
            # Alarm severity has been reset to 0 by handlers
            # Silently drop alarm
            logging.debug("Alarm severity is 0, dropping")
            a.delete()
            return
        # Launch jobs when necessary
        if a.alarm_class.id in self.alarm_jobs:
            for job in self.alarm_jobs[r.alarm_class.id]:
                job.submit(a)
        # Notify about new alarm
        if not a.root:
            a.managed_object.event(a.managed_object.EV_ALARM_RISEN, {
                "alarm": a,
                "subject": a.subject,
                "body": a.body,
                "symptoms": a.alarm_class.symptoms,
                "recommended_actions": a.alarm_class.recommended_actions,
                "probable_causes": a.alarm_class.probable_causes
            }, delay=a.alarm_class.get_notification_delay())

    def clear_alarm(self, r, e):
        managed_object = self.eval_expression(r.managed_object, event=e)
        if not managed_object:
            logging.debug("Empty managed object, ignoring")
            return
        if r.unique:
            discriminator, vars = r.get_vars(e)
            assert discriminator is not None
            a = ActiveAlarm.objects.filter(
                managed_object=managed_object.id,
                discriminator=discriminator).first()
            if a:
                logging.debug("%s: Event %s(%s) clears alarm %s(%s)" % (
                    r.u_name, str(e.id), e.event_class.name,
                    str(a.id), a.alarm_class.name))
                a.contribute_event(e, close=True)
                a.clear_alarm("Cleared by disposition rule '%s'" % r.u_name)

    def get_delayed_event(self, r, e):
        """
        Check wrether all delayed conditions are met

        :param r: Delayed rule
        :param e: Event which can trigger delayed rule
        """
        # @todo: Rewrite to scheduler
        discriminator, vars = r.get_vars(e)
        ws = e.timestamp - datetime.timedelta(seconds=r.combo_window)
        de = ActiveEvent.objects.filter(
                managed_object=e.managed_object_id,
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
                managed_object=e.managed_object_id,
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

    def eval_expression(self, expression, **kwargs):
        """
        Evaluate expression in given context
        """
        env = {
            "re": re,
            "utils": utils
        }
        env.update(kwargs)
        return eval(expression, {}, env)

    def dispose_event(self, e):
        """
        Dispose event according to disposition rule
        """
        drc = self.rules.get(e.event_class.id)
        if not drc:
            return
        # Apply disposition rules
        for r in drc:
            if r.conditional_pyrule:
                cond = r.conditional_pyrule(rule_name=r.name, event=e)
            else:
                cond = self.eval_expression(r.condition, event=e)
            if cond:
                # Process action
                if r.action == "drop":
                    e.delete()
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

if __name__ == "__main__":
    CorrelatorService().start()
