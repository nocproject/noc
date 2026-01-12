# ---------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python
import datetime
import operator
import re
import logging
from threading import Lock
from typing import Optional, List, Set, Union, Tuple, Dict, Any

# Third-party modules
from bson import ObjectId
from django.db import connection as pg_connection
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    DateTimeField,
    ListField,
    EmbeddedDocumentListField,
)
from mongoengine.errors import ValidationError
import cachetools
import orjson

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.model.decorator import on_save, on_delete
from noc.core.defer import call_later
from noc.core.change.decorator import change
from noc.core.watchers.types import ObjectEffect, WatchItem
from noc.core.watchers.decorator import watchers, WATCHER_JCLS, get_next_ts
from noc.core.mx import MessageType, send_message, MX_TO_STAGE_NAME
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.service import Service
from noc.sa.models.objectwatchersitem import WatchDocumentItem
from noc.inv.models.networksegment import NetworkSegment
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.remotesystem import RemoteSystem
from .maintenancetype import MaintenanceType

id_lock = Lock()
logger = logging.getLogger(__name__)


# Query for remove maintenance from affected structure
SQL_REMOVE = """
  UPDATE sa_managedobject
  SET affected_maintenances = affected_maintenances - %s
  WHERE affected_maintenances ? %s
"""
SCHEDULER = "scheduler"


class RemoteObject(EmbeddedDocument):
    model_id: str = StringField(
        required=True,
        choices=["sa.ManagedObject", "sa.Service", "inv.NetworkSegment"],
    )
    remote_id: str = StringField(required=True)
    name: str = StringField(required=False)

    def __str__(self):
        if self.name:
            return f"{self.model_id}@{self.remote_id} ({self.name})"
        return f"{self.model_id}@{self.remote_id}"


class MaintenanceService(EmbeddedDocument):
    service = ReferenceField(Service, required=True)
    include_object = BooleanField(default=False)

    def __str__(self):
        return f"{self.service}"


class MaintenanceObject(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject, required=True)

    def __str__(self):
        return f"{self.object}"


class MaintenanceSegment(EmbeddedDocument):
    segment = ReferenceField(NetworkSegment, required=True)

    def __str__(self):
        return f"{self.segment}"


@on_save
@change
@watchers
@on_delete
class Maintenance(Document):
    meta = {
        "collection": "noc.maintenance",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "start",
            "stop",
            ("start", "is_completed"),
            "administrative_domain",
            "is_completed",
            "watcher_wait_ts",
        ],
        "legacy_collections": ["noc.maintainance"],
    }

    type: MaintenanceType = ReferenceField(MaintenanceType, required=True)
    subject = StringField(required=True)
    description = StringField()
    start = DateTimeField(required=True)
    stop = DateTimeField(required=False)
    is_completed = BooleanField(default=False)
    auto_confirm = BooleanField(default=True)
    template = ForeignKeyField(Template)
    contacts = StringField()
    suppress_alarms = BooleanField()
    # Escalate TT during maintenance
    escalate_managed_object = ForeignKeyField(ManagedObject)
    # Time pattern when maintenance is active
    # None - active all the time
    time_pattern: Optional[TimePattern] = ForeignKeyField(TimePattern)
    # Objects declared to be affected by maintenance
    direct_objects: List["MaintenanceObject"] = EmbeddedDocumentListField(MaintenanceObject)
    # Segments declared to be affected by maintenance
    direct_segments: List["MaintenanceSegment"] = EmbeddedDocumentListField(MaintenanceSegment)
    #  Service declared to be affected by maintenance
    direct_services: List["MaintenanceService"] = EmbeddedDocumentListField(MaintenanceService)
    # direct_group =
    # All Administrative Domain for all affected objects
    administrative_domain = ListField(ForeignKeyField(AdministrativeDomain))
    # Escalated TT ID in form
    # <external system name>:<external tt id>
    escalation_tt = StringField(required=False)
    # @todo: Attachments
    escalation_policy = StringField(
        choices=[("E", "Enable"), ("D", "Disable"), ("S", "Suspend"), ("M", "Maintenance")],
        default="S",
    )
    #
    # Reference to remote system object has been imported from
    remote_system: Optional["RemoteSystem"] = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Array remote objects and service ids
    remote_objects: List["RemoteObject"] = EmbeddedDocumentListField(RemoteObject)
    # Watchers
    watchers: List[WatchDocumentItem] = EmbeddedDocumentListField(WatchDocumentItem)
    watcher_wait_ts: Optional[datetime.datetime] = DateTimeField(required=False)
    # Object id in BI
    # bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    MAINTENANCE_STOP_HANDLER = "noc.maintenance.models.maintenance.stop"
    MAINTENANCE_AFFECTED_HANDLER = "noc.maintenance.models.maintenance.update_affected_objects"
    SUPPORTED_EFFECTS = frozenset([ObjectEffect.WF_EVENT, ObjectEffect.MX_EVENT])

    def __str__(self):
        return f"[{'V' if self.is_completed else ' '}] {self.start}-{self.stop}: {self.subject}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Maintenance"]:
        return Maintenance.objects.filter(id=oid).first()

    @classmethod
    def get_min_wait_ts(cls) -> Optional[datetime.datetime]:
        """"""
        return (
            Maintenance.objects()
            .aggregate(
                [
                    {"$match": {"is_completed": {"$ne": True}}},
                    {"$group": {"_id": None, "wait_ts": {"$min": "$watcher_wait_ts"}}},
                ]
            )
            .next()["wait_ts"]
        )

    @property
    def is_active(self) -> bool:
        """"""
        if self.is_completed:
            return False
        now = datetime.datetime.now()
        if self.time_pattern and not self.time_pattern.match(now):
            return False
        if self.auto_confirm:
            return self.start <= now < self.stop
        return self.start <= now

    @property
    def active_interval(self) -> Tuple[datetime.datetime, datetime.datetime]:
        """For old fixes, String to datetime fields"""
        m_start, m_stop = self.start, self.stop
        if isinstance(m_start, str):
            m_start = datetime.datetime.fromisoformat(m_start)
        if isinstance(m_stop, str):
            m_stop = datetime.datetime.fromisoformat(m_stop)
        return m_start, m_stop

    def event(self, stage: str, data: Optional[Dict[str, Any]] = None):
        """
        Process object-related event
        Args:
            stage: on_start, on_end, on_stage
            data:
        """
        logger.info("[%s|%s] Sending maintenance event message", self.subject, stage)
        d = self.get_message_context()
        if data:
            d.update(data)
        send_message(
            data=d,
            message_type=MessageType.MAINTENANCE_PROCESSED,
            headers={MX_TO_STAGE_NAME: stage.encode()},
        )

    def get_message_context(self) -> Dict[str, Any]:
        """Service Message Ctx"""
        # Direct maintenance
        r = {
            "id": str(self.id),
            "subject": self.subject,
            "description": self.description,
            "is_completed": self.is_completed,
            "contacts": self.contacts,
            "type": {"id": str(self.type.id), "name": self.type.name},
        }
        if self.remote_system:
            r["remote_system"] = {
                "id": str(self.remote_system.id),
                "name": self.remote_system.name,
            }
            r["remote_id"] = self.remote_id
        # Affected ?
        return r

    def update_remote_objects(self, objects: List[Dict[str, Any]]):
        """Update remote Object"""
        r = []
        for o in objects:
            r.append(
                RemoteObject(model_id=o["model_id"], remote_id=o["remote_id"], name=o.get("name")),
            )
        self.remote_objects = r
        self.save()

    def sync_affected(self):
        """Add Maintenance to Affected Objects"""
        m_start, m_stop = self.active_interval
        # Affected Maintenances
        if not self.is_completed:
            call_later(
                self.MAINTENANCE_AFFECTED_HANDLER,
                60,
                maintenance_id=self.id,
                start=m_start,
                stop=m_stop if self.auto_confirm else None,
            )
        if (self.direct_services or self.remote_objects) and not self.is_completed:
            Service.update_maintenance(
                self.id,
                [ds.service for ds in self.direct_services],
                m_start,
                remote_system=self.remote_system,
                remote_ids=[
                    oo.remote_id for oo in self.remote_objects if oo.model_id == "sa.Service"
                ],
            )
        elif self.direct_services or self.remote_objects:
            Service.reset_maintenance(self.id)
        if (self.direct_objects or self.remote_objects) and not self.is_completed:
            ManagedObject.update_maintenance(
                self.id,
                [do.object for do in self.direct_objects],
                m_start,
                affected_topology=True,
                remote_system=self.remote_system,
                remote_ids=[
                    oo.remote_id for oo in self.remote_objects if oo.model_id == "sa.ManagedObject"
                ],
            )
        elif self.direct_objects or self.remote_objects:
            ManagedObject.reset_maintenance(self.id)

    def update_object_watchers(
        self,
        to_watchers: List[WatchItem],
        to_remove: Optional[List[Tuple[ObjectEffect, str, Optional[str]]]],
        dry_run: bool = False,
        bulk=None,
    ):
        """"""
        from noc.core.scheduler.scheduler import Scheduler

        updates = []
        up_w = {(w.effect, w.key, w.remote_system): w for w in to_watchers}
        for w in self.watchers:
            rs = w.remote_system.name if w.remote_system else None
            if to_remove and (w.effect, w.key, rs) in to_remove:
                continue
            update = up_w.pop((w.effect, w.key, rs), None)
            if update:
                w = WatchDocumentItem.from_item(update)
            updates.append(w)
        for w in up_w.values():
            rs = RemoteSystem.get_by_name(w.remote_system) if w.remote_system else None
            updates.append(WatchDocumentItem.from_item(w, remote_system=rs))
        self.watchers = updates
        if not updates:
            wait_ts = None
        else:
            wait_ts, _ = self.active_interval
        if self.watcher_wait_ts != wait_ts:
            self.watcher_wait_ts = wait_ts
        if dry_run or self._created:
            return
        m_ts = self.get_min_wait_ts()
        if wait_ts and (not m_ts or wait_ts < m_ts):
            scheduler = Scheduler(SCHEDULER)
            scheduler.submit(
                jcls=WATCHER_JCLS, key="maintenance.Maintenance", ts=get_next_ts(wait_ts)
            )
        set_op = {"watchers": self.watchers, "watcher_wait_ts": self.watcher_wait_ts}
        self.update(**set_op)

    def ensure_jobs(self):
        """Ensure maintenance Job"""
        now = datetime.datetime.now()
        m_start, m_stop = self.active_interval
        # Auto completed
        if self.auto_confirm and m_stop > now:
            delay = (m_stop - now).total_seconds()
            call_later(self.MAINTENANCE_STOP_HANDLER, delay, maintenance_id=self.id)

    def ensure_escalated_jobs(self):
        """Check maintenances jobs"""
        if not self.escalate_managed_object:
            return
        if not self.is_completed and self.auto_confirm:
            start, stop = self.active_interval
            call_later(
                "noc.services.escalator.maintenance.start_maintenance",
                delay=max(
                    (start - datetime.datetime.now()).total_seconds(),
                    60,
                ),
                scheduler="escalator",
                pool=self.escalate_managed_object.escalator_shard,
                maintenance_id=self.id,
            )
            if self.auto_confirm:
                call_later(
                    "noc.services.escalator.maintenance.close_maintenance",
                    delay=max(
                        (stop - datetime.datetime.now()).total_seconds(),
                        60,
                    ),
                    scheduler="escalator",
                    pool=self.escalate_managed_object.escalator_shard,
                    maintenance_id=self.id,
                )
        if self.is_completed and not self.auto_confirm:
            call_later(
                "noc.services.escalator.maintenance.close_maintenance",
                scheduler="escalator",
                pool=self.escalate_managed_object.escalator_shard,
                maintenance_id=self.id,
            )

    def clean(self):
        """Validate dereference"""
        if self.direct_objects:
            if any(o_elem.object is None for o_elem in self.direct_objects):
                raise ValidationError("Object line is Empty")
        if self.direct_segments:
            for elem in self.direct_segments:
                try:
                    elem.segment = elem.segment
                except Exception:
                    raise ValidationError("Segment line is Empty")

    def on_save(self):
        changed_fields = set()
        if hasattr(self, "_changed_fields"):
            changed_fields = set(self._changed_fields)
        if (not changed_fields or "is_completed" in changed_fields) and self.is_completed:
            self.remove_maintenance()
            self.event("on_completed")
        if (
            not changed_fields or "is_completed" in changed_fields or "start" in changed_fields
        ) and not self.is_completed:
            # Gen MX Event
            m_start, _ = self.active_interval
            self.add_watch(ObjectEffect.MX_EVENT, after=m_start, once=True, stage="start")
        self.sync_affected()
        self.ensure_escalated_jobs()
        self.ensure_jobs()

    def on_delete(self):
        self.remove_maintenance()

    def remove_maintenance(self):
        Service.reset_maintenance(self.id)
        ManagedObject.reset_maintenance(self.id)

    @classmethod
    def currently_affected(cls, objects: Optional[List[int]] = None) -> List[int]:
        """
        Returns a list of currently affected object ids
        """
        data = []
        now = datetime.datetime.now()
        for d in Maintenance._get_collection().find(
            {"start": {"$lte": now}, "stop": {"$gte": now}, "is_completed": False},
            {"_id": 1, "time_pattern": 1},
        ):
            if d.get("time_pattern"):
                # Restrict to time pattern
                tp = TimePattern.get_by_id(d["time_pattern"])
                if tp and not tp.match(now):
                    continue
            data.append(str(d["_id"]))
        affected = list(
            ManagedObject.objects.filter(
                is_managed=True, affected_maintenances__has_any_keys=data
            ).values_list("id", flat=True)
        )
        if objects:
            affected = list(set(affected) & set(objects))
        return affected


def update_affected_objects(
    maintenance_id, start: datetime.datetime, stop: Optional[datetime.datetime] = None
):
    """
    Calculate and fill affected objects
    """

    # All affected maintenance objects
    mai_objects: List[int] = list(
        ManagedObject.objects.filter(
            is_managed=True, affected_maintenances__has_key=str(maintenance_id)
        ).values_list("id", flat=True)
    )

    def get_downlinks(objects: Set[int]):
        # Get all additional objects which may be affected
        r = {
            mo_id
            for mo_id in ManagedObject.objects.filter(
                is_managed=True, uplinks__overlap=list(objects)
            ).values_list("id", flat=True)
            if mo_id not in objects
        }
        if not r:
            return r
        # Leave only objects with all uplinks affected
        rr = set()
        for mo_id, uplinks in ManagedObject.objects.filter(
            is_managed=True, id__in=list(r)
        ).values_list("id", "uplinks"):
            if len([1 for u in uplinks if u in objects]) == len(uplinks):
                rr.add(mo_id)
        return rr

    def get_segment_objects(segment):
        # Get objects belonging to segment
        so = set(
            ManagedObject.objects.filter(is_managed=True, segment=segment).values_list(
                "id", flat=True
            )
        )
        # Get objects from underlying segments
        for ns in NetworkSegment._get_collection().find({"parent": segment}, {"_id": 1}):
            so |= get_segment_objects(ns["_id"])
        return so

    data = Maintenance.get_by_id(maintenance_id)
    logger.info("[%s] Processed update Maintenance affected", data.id)
    # Calculate affected objects
    affected: Set[int] = {o.object.id for o in data.direct_objects if o.object}
    for o in data.direct_segments:
        if o.segment:
            affected |= get_segment_objects(o.segment.id)
    while True:
        r = get_downlinks(affected)
        if not r:
            break
        affected |= r
    # Calculate affected administrative_domain
    affected_ad = list(
        set(
            ManagedObject.objects.filter(is_managed=True, id__in=list(affected)).values_list(
                "administrative_domain__id", flat=True
            )
        )
    )

    # @todo: Calculate affected objects considering topology
    Maintenance._get_collection().update_one(
        {"_id": data.id},
        {"$set": {"administrative_domain": affected_ad}},
    )
    affected_data = {"start": start, "stop": stop}
    if data.time_pattern:
        affected_data["time_pattern"] = data.time_pattern.id
    with pg_connection.cursor() as cursor:
        # Cleanup Maintenance objects
        cursor.execute(SQL_REMOVE, [str(maintenance_id), str(maintenance_id)])
        # Add Maintenance objects
        SQL_ADD = """UPDATE sa_managedobject
        SET affected_maintenances = affected_maintenances || %s::jsonb
        WHERE id = ANY(%s::int[])"""
        cursor.execute(
            SQL_ADD,
            [
                orjson.dumps({str(maintenance_id): affected_data}).decode("utf-8"),
                list(affected),
            ],
        )
    # Clear cache
    for mo_id in set(mai_objects).union(affected):
        ManagedObject._reset_caches(mo_id)
    logger.info("[%s] Maintenance affected update completed", data.id)
    # Check id objects not in affected
    # nin_mai = set(affected).difference(set(mai_objects))
    # Check id objects for delete
    # in_mai = set(mai_objects).difference(set(affected))

    # if len(nin_mai) != 0 or len(in_mai) != 0:
    #     with pg_connection.cursor() as cursor:
    #         # Add Maintenance objects
    #         if len(nin_mai) != 0:
    #             SQL_ADD = """UPDATE sa_managedobject
    #             SET affected_maintenances = jsonb_insert(affected_maintenances,
    #             '{"%s"}', '{"start": "%s", "stop": "%s"}'::jsonb)
    #             WHERE id IN %s;""" % (
    #                 str(maintenance_id),
    #                 start,
    #                 stop,
    #                 "(%s)" % ", ".join(map(repr, nin_mai)),
    #             )
    #             cursor.execute(SQL_ADD)
    #         # Delete Maintenance objects
    #         if len(in_mai) != 0:
    #             SQL_REMOVE = """UPDATE sa_managedobject
    #                  SET affected_maintenances = affected_maintenances #- '{%s}'
    #                  WHERE id IN %s AND affected_maintenances @> '{"%s": {}}';""" % (
    #                 str(maintenance_id),
    #                 "(%s)" % ", ".join(map(repr, in_mai)),
    #                 str(maintenance_id),
    #             )
    #             cursor.execute(SQL_REMOVE)


def stop(maintenance_id):
    rx_mail = re.compile(r"(?P<mail>[A-Za-z0-9\.\_\-]+\@[A-Za-z0-9\@\.\_\-]+)", re.MULTILINE)
    # Find Active Maintenance
    mai = Maintenance.get_by_id(maintenance_id)
    if not mai:
        logger.warning("Stop for maintenance with Unknown Id: %s", maintenance_id)
        return
    logger.info("[%s] Run stop Maintenance Job", mai)
    mai.is_completed = True
    # Find email addresses on Maintenance Contacts
    if mai.template:
        ctx = {"maintenance": mai}
        contacts = rx_mail.findall(mai.contacts)
        if contacts:
            # Create message
            subject = mai.template.render_subject(**ctx)
            body = mai.template.render_body(**ctx)
            for mail in contacts:
                nf = NotificationGroup()
                nf.send_notification(
                    "mail",
                    mail,
                    subject,
                    body,
                )
    Maintenance._get_collection().update_many(
        {"_id": maintenance_id}, {"$set": {"is_completed": True}}
    )
    mai_objects: List[int] = list(
        ManagedObject.objects.filter(
            is_managed=True, affected_maintenances__has_key=str(maintenance_id)
        ).values_list("id", flat=True)
    )
    ManagedObject.reset_maintenance(maintenance_id)
    # Clear cache
    for mo_id in mai_objects:
        ManagedObject._reset_caches(mo_id)
