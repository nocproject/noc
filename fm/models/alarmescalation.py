# ---------------------------------------------------------------------
# AlarmEscalation model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import operator
from threading import Lock
import datetime
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    BooleanField,
)
import cachetools

# NOC modules
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.ttsystem import TTSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.mongo.fields import ForeignKeyField
from noc.core.defer import call_later

logger = logging.getLogger(__name__)
ac_lock = Lock()
id_lock = Lock()


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
    resource_group = ReferenceField(ResourceGroup)
    time_pattern = ForeignKeyField(TimePattern)
    min_severity = IntField(default=0)
    # Action part
    notification_group = ForeignKeyField(NotificationGroup)
    template = ForeignKeyField(Template)
    clear_template = ForeignKeyField(Template)
    create_tt = BooleanField(default=False)
    promote_group_tt = BooleanField(default=True)
    promote_affected_tt = BooleanField(default=True)
    close_tt = BooleanField(default=False)
    wait_tt = BooleanField(default=False)
    # Stop or continue to next rule
    stop_processing = BooleanField(default=False)


class AlarmEscalation(Document):
    """
    Alarm escalations
    """

    meta = {"collection": "noc.alarmescalatons", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    alarm_classes = ListField(EmbeddedDocumentField(AlarmClassItem))
    pre_reasons = ListField(EmbeddedDocumentField(PreReasonItem))
    escalations = ListField(EmbeddedDocumentField(EscalationItem))
    global_limit = IntField()
    max_escalation_retries = IntField(default=30)  # @fixme make it configurable

    _ac_cache = cachetools.TTLCache(maxsize=1000, ttl=300)
    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AlarmEscalation"]:
        return AlarmEscalation.objects.filter(id=oid).first()

    @property
    def delays(self):
        if not hasattr(self, "_delays"):
            self._delays = sorted(set(e.delay for e in self.escalations))
        return self._delays

    def get_pre_reason(self, tt_system):
        if not hasattr(self, "_prc"):
            self._prc = {r.tt_system.id: r.pre_reason for r in self.pre_reasons}
        return self._prc.get(tt_system.id)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ac_cache"), lock=lambda _: ac_lock)
    def get_class_escalations(cls, alarm_class):
        if hasattr(alarm_class, "id"):
            alarm_class = alarm_class.id
        return list(AlarmEscalation.objects.filter(alarm_classes__alarm_class=alarm_class))

    @classmethod
    def watch_escalations(
        cls,
        alarm,
        force: bool = False,
        timestamp_policy: str = "a",
        defer: bool = True,
        prev_escalation: Optional[str] = None,
    ):
        if alarm.alarm_class.is_ephemeral:
            # Ephemeral alarm has not escalated
            return
        now = datetime.datetime.now()
        for esc in cls.get_class_escalations(alarm.alarm_class):
            for e_item in esc.escalations:
                # Check administrative domain
                if (
                    e_item.administrative_domain
                    and e_item.administrative_domain.id not in alarm.adm_path
                ):
                    continue
                # Check severity
                if e_item.min_severity and alarm.severity < e_item.min_severity:
                    continue
                # Check ResourceGroup
                if e_item.resource_group and alarm.managed_object not in e_item.resource_group:
                    continue
                logger.debug("[%s] Watch for %s after %s seconds", alarm.id, esc.name, e_item.delay)
                et = alarm.timestamp + datetime.timedelta(seconds=e_item.delay)
                if timestamp_policy == "c":
                    # If escalation with current timestamp - shift consequence after main escalation
                    delay = max((et - now).total_seconds(), 120) + 120 if et > now else 120
                    logger.info(
                        "[%s] Watch escalation with create new timestamp policy, after %s seconds",
                        alarm.id,
                        delay,
                    )
                elif et > now:
                    # A delay is needed for the alarm tree to assemble
                    delay = 60 if force else (et - now).total_seconds()
                else:
                    delay = None
                if defer:
                    call_later(
                        "noc.services.escalator.escalation.escalate",
                        scheduler="escalator",
                        pool=alarm.managed_object.escalator_shard,
                        delay=delay,
                        max_runs=esc.max_escalation_retries,
                        alarm_id=alarm.id,
                        escalation_id=esc.id,
                        escalation_delay=e_item.delay,
                        force=force,
                        timestamp_policy=timestamp_policy,
                        prev_escalation=prev_escalation,
                    )
                else:
                    from noc.services.escalator.escalation import escalate

                    escalate(
                        alarm_id=alarm.id,
                        escalation_id=esc.id,
                        escalation_delay=e_item.delay,
                        force=force,
                        timestamp_policy=timestamp_policy,
                        prev_escalation=prev_escalation,
                    )
                if e_item.stop_processing:
                    break
