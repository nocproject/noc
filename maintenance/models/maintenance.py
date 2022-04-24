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


class MaintenanceObject(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject)


class MaintenanceSegment(EmbeddedDocument):
    segment = ReferenceField(NetworkSegment)


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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
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
        if (
            hasattr(self, "_changed_fields")
            and "direct_objects" in self._changed_fields
            or hasattr(self, "_changed_fields")
            and "direct_segments" in self._changed_fields
        ):
            self.update_affected_objects_maintenance()

        if hasattr(self, "_changed_fields") and "stop" in self._changed_fields:
            if not self.is_completed and self.auto_confirm:
                self.auto_confirm_maintenance()

        if hasattr(self, "_changed_fields") and "is_completed" in self._changed_fields:
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
        SQL = """UPDATE sa_managedobject
                 SET affected_maintenances = affected_maintenances #- '{%s}'
                 WHERE affected_maintenances @> '{"%s": {}}';""" % (
            str(self.id),
            str(self.id),
        )
        with pg_connection.cursor() as cursor:
            cursor.execute(SQL)

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


def update_affected_objects(maintenance_id, start, stop=None):
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
    # Calculate affected objects
    affected: Set[int] = set(o.object.id for o in data.direct_objects if o.object)
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
    # Check id objects not in affected
    nin_mai = set(affected).difference(set(mai_objects))
    # Check id objects for delete
    in_mai = set(mai_objects).difference(set(affected))

    if len(nin_mai) != 0 or len(in_mai) != 0:
        with pg_connection.cursor() as cursor:
            # Add Maintenance objects
            if len(nin_mai) != 0:
                SQL_ADD = """UPDATE sa_managedobject
                SET affected_maintenances = jsonb_insert(affected_maintenances,
                '{"%s"}', '{"start": "%s", "stop": "%s"}'::jsonb)
                WHERE id IN %s;""" % (
                    str(maintenance_id),
                    start,
                    stop,
                    "(%s)" % ", ".join(map(repr, nin_mai)),
                )
                cursor.execute(SQL_ADD)
            # Delete Maintenance objects
            if len(in_mai) != 0:
                SQL_REMOVE = """UPDATE sa_managedobject
                     SET affected_maintenances = affected_maintenances #- '{%s}'
                     WHERE id IN %s AND affected_maintenances @> '{"%s": {}}';""" % (
                    str(maintenance_id),
                    "(%s)" % ", ".join(map(repr, in_mai)),
                    str(maintenance_id),
                )
                cursor.execute(SQL_REMOVE)
        # Clear cache
        for mo_id in mai_objects:
            ManagedObject._reset_caches(mo_id)


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
    Maintenance._get_collection().update({"_id": maintenance_id}, {"$set": {"is_completed": True}})
    mai_objects: List[int] = list(
        ManagedObject.objects.filter(
            is_managed=True, affected_maintenances__has_key=str(maintenance_id)
        ).values_list("id", flat=True)
    )
    SQL = """UPDATE sa_managedobject
             SET affected_maintenances = affected_maintenances #- '{%s}'
             WHERE affected_maintenances @> '{"%s": {}}';""" % (
        maintenance_id,
        maintenance_id,
    )
    with pg_connection.cursor() as cursor:
        cursor.execute(SQL)
    # Clear cache
    for mo_id in mai_objects:
        ManagedObject._reset_caches(mo_id)
