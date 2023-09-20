# ---------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python
import datetime
import operator
import re
import logging
from threading import Lock
from typing import Optional, List, Set

# Third-party modules
from django.db import connection as pg_connection
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ReferenceField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
)
import cachetools
import orjson

# NOC modules
from .maintenancetype import MaintenanceType
from mongoengine.errors import ValidationError
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.core.mongo.fields import ForeignKeyField
from noc.core.model.decorator import on_save, on_delete
from noc.main.models.timepattern import TimePattern
from noc.main.models.template import Template
from noc.core.defer import call_later
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.main.models.notificationgroup import NotificationGroup

id_lock = Lock()

logger = logging.getLogger(__name__)

# Query for remove maintenance from affected structure
SQL_REMOVE = """
  UPDATE sa_managedobject
  SET affected_maintenances = affected_maintenances - %s
  WHERE affected_maintenances ? %s
"""


class MaintenanceObject(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject)

    def __str__(self):
        return f"{self.object}"


class MaintenanceSegment(EmbeddedDocument):
    segment = ReferenceField(NetworkSegment)

    def __str__(self):
        return f"{self.segment}"


@on_save
@on_delete
class Maintenance(Document):
    meta = {
        "collection": "noc.maintenance",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["start", "stop", ("start", "is_completed"), "administrative_domain"],
        "legacy_collections": ["noc.maintainance"],
    }

    type = ReferenceField(MaintenanceType)
    subject = StringField(required=True)
    description = StringField()
    start = DateTimeField()
    stop = DateTimeField()
    is_completed = BooleanField(default=False)
    auto_confirm = BooleanField(default=True)
    template = ForeignKeyField(Template)
    contacts = StringField()
    suppress_alarms = BooleanField()
    # Escalate TT during maintenance
    escalate_managed_object = ForeignKeyField(ManagedObject)
    # Time pattern when maintenance is active
    # None - active all the time
    time_pattern = ForeignKeyField(TimePattern)
    # Objects declared to be affected by maintenance
    direct_objects = ListField(EmbeddedDocumentField(MaintenanceObject))
    # Segments declared to be affected by maintenance
    direct_segments = ListField(EmbeddedDocumentField(MaintenanceSegment))
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return f"[{'V' if self.is_completed else ' '}] {self.start}-{self.stop}: {self.subject}"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> "Maintenance":
        return Maintenance.objects.filter(id=id).first()

    def update_affected_objects_maintenance(self):
        call_later(
            "noc.maintenance.models.maintenance.update_affected_objects",
            60,
            maintenance_id=self.id,
            start=self.start,
            stop=self.stop if self.auto_confirm else None,
        )

    def auto_confirm_maintenance(self):
        st = str(self.stop)
        if "T" in st:
            st = st.replace("T", " ")
        stop = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        if stop > now:
            delay = (stop - now).total_seconds()
            call_later("noc.maintenance.models.maintenance.stop", delay, maintenance_id=self.id)

    def save(self, *args, **kwargs):
        created = False
        if self._created:
            created = self._created
        if self.direct_objects:
            if any(o_elem.object is None for o_elem in self.direct_objects):
                raise ValidationError("Object line is Empty")
        if self.direct_segments:
            for elem in self.direct_segments:
                try:
                    elem.segment = elem.segment
                except Exception:
                    raise ValidationError("Segment line is Empty")
        super().save(*args, **kwargs)
        if created and (self.direct_objects or self.direct_segments):
            self.update_affected_objects_maintenance()
        if self.auto_confirm:
            self.auto_confirm_maintenance()

    def on_save(self):
        changed_fields = set()
        if hasattr(self, "_changed_fields"):
            changed_fields = set(self._changed_fields)
        if changed_fields.intersection(
            {"direct_objects", "direct_segments", "stop", "start", "time_pattern"}
        ):
            self.update_affected_objects_maintenance()
        if "stop" in changed_fields:
            if not self.is_completed and self.auto_confirm:
                self.auto_confirm_maintenance()
        if "is_completed" in changed_fields:
            self.remove_maintenance()

        if self.escalate_managed_object:
            if not self.is_completed and self.auto_confirm:
                call_later(
                    "noc.services.escalator.maintenance.start_maintenance",
                    delay=max(
                        (self.start - datetime.datetime.now()).total_seconds(),
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
                            (self.stop - datetime.datetime.now()).total_seconds(),
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

    def on_delete(self):
        self.remove_maintenance()

    def remove_maintenance(self):
        with pg_connection.cursor() as cursor:
            cursor.execute(SQL_REMOVE, [str(self.id), str(self.id)])

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


def update_affected_objects(maintenance_id: str, **kwargs):
    def get_object_downlinks(mo_ids):
        """

        :return:
        """
        with pg_connection.cursor() as cursor:
            cursor.execute(
                """
                WITH RECURSIVE r AS (
                    SELECT id, uplinks
                    FROM sa_managedobject
                    WHERE id = ANY(%s)
                    UNION
                    SELECT sa.id, sa.uplinks
                    FROM sa_managedobject AS sa JOIN r ON r.id = ANY(sa.uplinks)
                )
                SELECT id FROM r;
            """,
                [mo_ids],
            )
            return [r[0] for r in cursor]

    maintenance = Maintenance.get_by_id(maintenance_id)
    if not maintenance:
        logger.error("[%s] Unknown Maintenance", maintenance_id)
        return
    logger.info("[%s] Calculate affected", maintenance_id)
    # Calculate affected
    affected_segments = []
    for ds in maintenance.direct_segments:
        affected_segments += [str(r) for r in ds.segment.get_nested_ids()]
    affected_objects = get_object_downlinks([o.object.id for o in maintenance.direct_objects])
    # Calculate affected administrative_domain
    affected_ad = (
        ManagedObject.objects.filter(segment__in=affected_segments)
        .distinct("administrative_domain")
        .values_list("administrative_domain", flat=True)
    )

    # Update effective_maintenance
    affected_data = {"start": maintenance.start, "stop": maintenance.stop}
    if maintenance.time_pattern:
        affected_data["time_pattern"] = maintenance.time_pattern.id
    # Maintenance.objects.filter(id=maintenance_id).update_one(administrative_domain=affected_ad)
    logger.info(
        "[%s] Update affected maintenance objects: %s/%s",
        maintenance_id,
        len(affected_objects),
        len(affected_segments),
    )
    condition = ""
    with pg_connection.cursor() as cursor:
        SQL_ADD = """
            UPDATE sa_managedobject
            SET affected_maintenances = affected_maintenances || %s::jsonb
            WHERE segment = ANY(%s::text[])
            RETURNING id
        """
        cursor.execute(
            SQL_ADD,
            [
                orjson.dumps({str(maintenance.id): affected_data}).decode("utf-8"),
                affected_segments
            ]
        )
        updated = [r[0] for r in cursor]
        logger.info("[%s] Updated ids: %s", maintenance_id, len(updated))
        if updated:
            cursor.execute("""SELECT gin_clean_pending_list('sa_managedobject_affected_maintenances_idx')""")
            cursor.execute("""
              UPDATE sa_managedobject
              SET affected_maintenances = affected_maintenances - %s
              WHERE affected_maintenances ? %s AND NOT (id = ANY(%s::int[]))
            """, [str(maintenance.id), str(maintenance.id), updated])
        logger.info("[%s] End affected_maintenance updated", maintenance_id)


def stop(maintenance_id):
    rx_mail = re.compile(r"(?P<mail>[A-Za-z0-9\.\_\-]+\@[A-Za-z0-9\@\.\_\-]+)", re.MULTILINE)
    # Find Active Maintenance
    mai = Maintenance.get_by_id(maintenance_id)
    if not mai:
        return
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
    with pg_connection.cursor() as cursor:
        cursor.execute(SQL_REMOVE, [str(maintenance_id), str(maintenance_id)])
    # Clear cache
    for mo_id in mai_objects:
        ManagedObject._reset_caches(mo_id)
