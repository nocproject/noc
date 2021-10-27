# ---------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python
import datetime
import dateutil.parser
import operator
import re
from threading import Lock

# Third-party modules
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
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.model.decorator import on_save, on_delete_check
from noc.sa.models.objectdata import ObjectData
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
@on_delete_check(
    clean=[("maintenance.AffectedObjects", "maintenance")],
)
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
        )

    def auto_confirm_maintenance(self):
        stop = datetime.datetime.strptime(self.stop, "%Y-%m-%dT%H:%M:%S")
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
            AffectedObjects._get_collection().remove({"maintenance": self.id})

        if self.escalate_managed_object:
            if not self.is_completed and self.auto_confirm:
                call_later(
                    "noc.services.escalator.maintenance.start_maintenance",
                    delay=max(
                        (
                            dateutil.parser.parse(self.start) - datetime.datetime.now()
                        ).total_seconds(),
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
                            (
                                dateutil.parser.parse(self.stop) - datetime.datetime.now()
                            ).total_seconds(),
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

    @classmethod
    def currently_affected(cls):
        """
        Returns a list of currently affected object ids
        """
        affected = set()
        now = datetime.datetime.now()
        for d in cls._get_collection().find(
            {"start": {"$lte": now}, "stop": {"$gte": now}, "is_completed": False},
            {"_id": 1, "time_pattern": 1},
        ):
            if d.get("time_pattern"):
                # Restrict to time pattern
                tp = TimePattern.get_by_id(d["time_pattern"])
                if tp and not tp.match(now):
                    continue
            data = [
                {"$match": {"maintenance": d["_id"]}},
                {
                    "$project": {"_id": 0, "objects": "$affected_objects.object"},
                },
            ]
            for x in AffectedObjects._get_collection().aggregate(data):
                affected.update(x["objects"])
        return list(affected)

    @classmethod
    def get_object_maintenance(cls, mo):
        """
        Returns a list of active maintenance for object
        :param mo: Managed Object instance
        :return: List of Maintenance instances or empty list
        """
        r = []
        now = datetime.datetime.now()
        for m in Maintenance.objects.filter(start__lte=now, is_completed=False).order_by("start"):
            if m.time_pattern and not m.time_pattern.match(now):
                continue
            if AffectedObjects.objects.filter(maintenance=m, affected_objects__object=mo.id):
                r += [m]
        return r


class AffectedObjects(Document):
    meta = {
        "collection": "noc.affectedobjects",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["affected_objects.object"],
    }
    maintenance = PlainReferenceField(Maintenance)
    affected_objects = ListField(EmbeddedDocumentField(MaintenanceObject))


def update_affected_objects(maintenance_id):
    """
    Calculate and fill affected objects
    """

    def get_downlinks(objects):
        r = set()
        # Get all additional objects which may be affected
        for d in ObjectData._get_collection().find({"uplinks": {"$in": list(objects)}}, {"_id": 1}):
            if d["_id"] not in objects:
                r.add(d["_id"])
        if not r:
            return r
        # Leave only objects with all uplinks affected
        rr = set()
        for d in ObjectData._get_collection().find(
            {"_id": {"$in": list(r)}}, {"_id": 1, "uplinks": 1}
        ):
            if len([1 for u in d["uplinks"] if u in objects]) == len(d["uplinks"]):
                rr.add(d["_id"])
        return rr

    def get_segment_objects(segment):
        # Get objects belonging to segment
        so = set(ManagedObject.objects.filter(segment=segment).values_list("id", flat=True))
        # Get objects from underlying segments
        for ns in NetworkSegment._get_collection().find({"parent": segment}, {"_id": 1}):
            so |= get_segment_objects(ns["_id"])
        return so

    data = Maintenance.get_by_id(maintenance_id)
    # Calculate affected objects
    affected = set(o.object.id for o in data.direct_objects if o.object)
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
            ManagedObject.objects.filter(id__in=list(affected)).values_list(
                "administrative_domain__id", flat=True
            )
        )
    )

    # @todo: Calculate affected objects considering topology
    affected = [{"object": o} for o in sorted(affected)]
    Maintenance._get_collection().update(
        {"_id": maintenance_id},
        {"$set": {"administrative_domain": affected_ad}},
    )
    AffectedObjects._get_collection().update(
        {"maintenance": maintenance_id}, {"$set": {"affected_objects": affected}}, upsert=True
    )


def stop(maintenance_id):
    rx_mail = re.compile(r"(?P<mail>[A-Za-z0-9\.\_\-]+\@[A-Za-z0-9\@\.\_\-]+)", re.MULTILINE)
    # Find Active Maintenance
    mai = Maintenance.get_by_id(maintenance_id)
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
    AffectedObjects._get_collection().remove({"maintenance": maintenance_id})
