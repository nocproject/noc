# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmEscalation model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import operator
from threading import Lock
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, IntField, ReferenceField,
                                ListField, EmbeddedDocumentField,
                                BooleanField)
import cachetools
## NOC modules
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.ttsystem import TTSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.lib.nosql import ForeignKeyField
from noc.core.defer import call_later

logger = logging.getLogger(__name__)
ac_lock = Lock()


class AlarmClassItem(EmbeddedDocument):
    alarm_class = ReferenceField(AlarmClass)


class PreReasonItem(EmbeddedDocument):
    tt_system = ReferenceField(TTSystem)
    pre_reason = StringField()


class EscalationItem(EmbeddedDocument):
    # Delay part
    delay = IntField()
    # Match part
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    selector = ForeignKeyField(ManagedObjectSelector)
    time_pattern = ForeignKeyField(TimePattern)
    min_severity = IntField(default=0)
    # Action part
    notification_group = ForeignKeyField(NotificationGroup)
    template = ForeignKeyField(Template)
    clear_template = ForeignKeyField(Template)
    create_tt = BooleanField(default=False)
    close_tt = BooleanField(default=False)
    wait_tt = BooleanField(default=False)
    # Stop or continue to next rule
    stop_processing = BooleanField(default=False)


class AlarmEscalation(Document):
    """
    Alarm escalations
    """
    meta = {
        "collection": "noc.alarmescalatons",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    description = StringField()
    alarm_classes = ListField(EmbeddedDocumentField(AlarmClassItem))
    pre_reasons = ListField(EmbeddedDocumentField(PreReasonItem))
    escalations = ListField(EmbeddedDocumentField(EscalationItem))
    global_limit = IntField()

    _ac_cache = cachetools.TTLCache(maxsize=1000, ttl=300)

    def __unicode__(self):
        return self.name

    @property
    def delays(self):
        if not hasattr(self, "_delays"):
            self._delays = sorted(set(e.delay for e in self.escalations))
        return self._delays

    def get_pre_reason(self, tt_system):
        if not hasattr(self, "_prc"):
            self._prc = dict((r.tt_system.id, r.pre_reason) for r in self.pre_reasons)
        return self._prc.get(tt_system.id)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ac_cache"), lock=lambda _: ac_lock)
    def get_class_escalations(cls, alarm_class):
        if hasattr(alarm_class, "id"):
            alarm_class = alarm_class.id
        return list(
            AlarmEscalation.objects.filter(
                alarm_classes__alarm_class=alarm_class
            )
        )

    @classmethod
    def watch_escalations(cls, alarm):
        for esc in cls.get_class_escalations(alarm.alarm_class):
            for delay in esc.delays:
                logger.debug(
                    "[%s] Watch for %s after %s seconds",
                    alarm.id, esc.name, delay
                )
                call_later(
                    "noc.services.correlator.escalation.escalate",
                    pool=alarm.managed_object.pool.name,
                    delay=delay,
                    scheduler="correlator",
                    alarm_id=alarm.id,
                    escalation_id=esc.id,
                    escalation_delay=delay
                )
