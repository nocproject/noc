# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmDiagnosticConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock
from collections import defaultdict
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, ReferenceField, IntField
import cachetools
# NOC modules
from noc.sa.models.action import Action
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.lib.nosql import ForeignKeyField
from noc.sa.models.selectorcache import SelectorCache
from noc.core.defer import call_later
from noc.core.handler import get_handler
from noc.core.debug import error_report
from .alarmclass import AlarmClass
from .alarmdiagnostic import AlarmDiagnostic
from .utils import get_alarm
from noc.core.scheduler.job import Job


ac_lock = Lock()
logger = logging.getLogger(__name__)

PERIODIC_JOB_MAX_RUNS = 5


class AlarmDiagnosticConfig(Document):
    meta = {
        "collection": "noc.alarmdiagnosticconfig",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "alarm_class"
        ]
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    alarm_class = ReferenceField(AlarmClass)
    selector = ForeignKeyField(ManagedObjectSelector)
    # Process only on root cause
    only_root = BooleanField(default=True)
    # On alarm raise actions
    enable_on_raise = BooleanField(default=True)
    on_raise_header = StringField()
    on_raise_delay = IntField(default=0)
    on_raise_script = StringField()
    on_raise_action = ReferenceField(Action)
    on_raise_handler = StringField()
    # Periodic actions
    enable_periodic = BooleanField(default=True)
    periodic_header = StringField()
    periodic_interval = IntField(default=0)
    periodic_script = StringField()
    periodic_action = ReferenceField(Action)
    periodic_handler = StringField()
    # Clear actions
    enable_on_clear = BooleanField(default=True)
    on_clear_header = StringField()
    on_clear_delay = IntField(default=0)
    on_clear_script = StringField()
    on_clear_action = ReferenceField(Action)
    on_clear_handler = StringField()

    _ac_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ac_cache"),
                             lock=lambda _: ac_lock)
    def get_class_diagnostics(cls, alarm_class):
        return list(AlarmDiagnosticConfig.objects.filter(
            alarm_class=alarm_class.id,
            is_active=True
        ))

    @classmethod
    def on_raise(cls, alarm):
        """
        Submit raise and periodic jobs
        :param alarm:
        :return:
        """
        r_cfg = defaultdict(list)
        p_cfg = defaultdict(list)
        for c in cls.get_class_diagnostics(alarm.alarm_class):
            if c.selector and not SelectorCache.is_in_selector(
                    alarm.managed_object, c.selector
            ):
                continue
            if c.only_root and alarm.root:
                continue
            if c.enable_on_raise:
                if c.on_raise_script:
                    r_cfg[c.on_raise_delay] += [{
                        "script": c.on_raise_script,
                        "header": c.on_raise_header
                    }]
                if c.on_raise_action:
                    r_cfg[c.on_raise_delay] += [{
                        "action": c.on_raise_action.name,
                        "header": c.on_raise_header
                    }]
                if c.on_raise_handler:
                    r_cfg[c.on_raise_delay] += [{
                        "handler": c.on_raise_handler,
                        "header": c.on_raise_header
                    }]
            if c.enable_periodic:
                if c.periodic_script:
                    p_cfg[c.periodic_interval] += [{
                        "script": c.periodic_script,
                        "header": c.periodic_header
                    }]
                if c.periodic_action:
                    p_cfg[c.periodic_interval] += [{
                        "action": c.periodic_action.name,
                        "header": c.periodic_header
                    }]
                if c.periodic_handler:
                    p_cfg[c.periodic_interval] += [{
                        "handler": c.periodic_handler,
                        "header": c.periodic_header
                    }]
        # Submit on_raise job
        for delay in r_cfg:
            call_later(
                "noc.fm.models.alarmdiagnosticconfig.on_raise",
                scheduler="correlator",
                pool=alarm.managed_object.pool.name,
                delay=delay,
                alarm=alarm.id,
                cfg=r_cfg[delay]
            )
        # Submit periodic job
        for delay in p_cfg:
            call_later(
                "noc.fm.models.alarmdiagnosticconfig.periodic",
                scheduler="correlator",
                max_runs=PERIODIC_JOB_MAX_RUNS,
                pool=alarm.managed_object.pool.name,
                delay=delay,
                alarm=alarm.id,
                cfg={"cfg": p_cfg[delay], "delay": delay}
            )

        # @todo: Submit periodic job

    @classmethod
    def on_clear(cls, alarm):
        """
        Submit clear jobs
        :param alarm:
        :return:
        """
        cfg = defaultdict(list)
        for c in cls.get_class_diagnostics(alarm.alarm_class):
            if c.selector and not SelectorCache.is_in_selector(
                    alarm.managed_object, c.selector
            ):
                continue
            if c.only_root and alarm.root:
                continue
            if c.enable_on_clear:
                if c.on_clear_script:
                    cfg[c.on_clear_delay] += [{
                        "script": c.on_clear_script,
                        "header": c.on_clear_header
                    }]
                if c.on_clear_action:
                    cfg[c.on_clear_delay] += [{
                        "action": c.on_clear_action.id,
                        "header": c.on_clear_header
                    }]
                if c.on_clear_handler:
                    cfg[c.on_clear_delay] += [{
                        "handler": c.on_clear_handler,
                        "header": c.on_clear_header
                    }]
        # Submit on_clear job
        for delay in cfg:
            call_later(
                "noc.fm.models.alarmdiagnosticconfig.on_clear",
                scheduler="correlator",
                pool=alarm.managed_object.pool.name,
                delay=delay,
                alarm=alarm.id,
                cfg=cfg[delay]
            )
        AlarmDiagnostic.clear_diagnostics(alarm)

    @staticmethod
    def get_diag(alarm, cfg, state):
        mo = alarm.managed_object
        if not mo:
            return
        result = []
        for c in cfg:
            if c.get("header"):
                result += [c["header"].strip()]
            if "script" in c:
                logger.info("[%s] Running script %s", alarm.id, c["script"])
                try:
                    g = getattr(mo.scripts, c["script"])
                    result += [g()]
                except Exception as e:
                    error_report()
                    result += [str(e)]
            if "action" in c:
                logger.info("[%s] Running action %s", alarm.id, c["action"])
                try:
                    g = getattr(mo.actions, c["action"])
                    result += [g()]
                except Exception as e:
                    error_report()
                    result += [str(e)]
            if "handler" in c:
                logger.info("[%s] Running handler %s", alarm.id, c["handler"])
                try:
                    h = get_handler(c["handler"])
                    try:
                        result += [h(alarm)]
                    except Exception as e:
                        error_report()
                        result += [str(e)]
                except ImportError:
                    result += ["Invalid handler: %s" % c["handler"]]
        if result:
            AlarmDiagnostic.save_diagnostics(alarm, result, state)


def on_raise(alarm, cfg, *args, **kwargs):
    a = get_alarm(alarm)
    if not a:
        logger.info("[%s] Alarm is not found, skipping", alarm)
        return
    if a.status == "C":
        logger.info("[%s] Alarm is closed, skipping", alarm)
        return
    AlarmDiagnosticConfig.get_diag(a, cfg, "R")


def periodic(alarm, cfg, *args, **kwargs):
    a = get_alarm(alarm)
    if not a:
        logger.info("[%s] Alarm is not found, skipping", alarm)
        return
    if a.status == "C":
        logger.info("[%s] Alarm is closed, skipping", alarm)
        return
    AlarmDiagnosticConfig.get_diag(a, cfg["cfg"], "R")
    if cfg.get("delay"):
        Job.retry_after(delay=cfg["delay"])


def on_clear(alarm, cfg, *args, **kwargs):
    a = get_alarm(alarm)
    if not a:
        logger.info("[%s] Alarm is not found, skipping", alarm)
    AlarmDiagnosticConfig.get_diag(a, cfg, "C")
