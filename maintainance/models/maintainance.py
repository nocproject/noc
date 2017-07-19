# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Maintainance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python
import datetime
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, BooleanField, ReferenceField, DateTimeField,
    ListField, EmbeddedDocumentField
)
import cachetools
# NOC modules
from maintainancetype import MaintainanceType
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_save
from noc.sa.models.objectdata import ObjectData
from noc.main.models.timepattern import TimePattern
from noc.core.defer import call_later

id_lock = Lock()


class MaintainanceObject(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject)


class MaintainanceSegment(EmbeddedDocument):
    segment = ReferenceField(NetworkSegment)


@on_save
class Maintainance(Document):
    meta = {
        "collection": "noc.maintainance",
        "indexes": [
            "affected_objects.object",
            ("start", "is_completed")
        ]
    }

    type = ReferenceField(MaintainanceType)
    subject = StringField(required=True)
    description = StringField()
    start = DateTimeField()
    stop = DateTimeField()
    is_completed = BooleanField(default=False)
    contacts = StringField()
    suppress_alarms = BooleanField()
    # Escalate TT during maintenance
    escalate_managed_object = ForeignKeyField(ManagedObject)
    # Time pattern when maintenance is active
    # None - active all the time
    time_pattern = ForeignKeyField(TimePattern)
    # Objects declared to be affected by maintenance
    direct_objects = ListField(EmbeddedDocumentField(MaintainanceObject))
    # Segments declared to be affected by maintenance
    direct_segments = ListField(EmbeddedDocumentField(MaintainanceSegment))
    # All objects affected by maintenance
    affected_objects = ListField(EmbeddedDocumentField(MaintainanceObject))
    # Escalated TT ID in form
    # <external system name>:<external tt id>
    escalation_tt = StringField(required=False)
    # @todo: Attachments

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Maintainance.objects.filter(id=id).first()

    def on_save(self):
        self.update_affected_objects()
        if self.escalate_managed_object:
            if self.is_completed:
                call_later(
                    "noc.services.escalator.maintenance.start_maintenance",
                    delay=self.start - datetime.datetime.now(),
                    scheduler="escalator",
                    pool=self.escalate_managed_object.escalator_shard,
                    maintenance_id=self.id
                )
            else:
                call_later(
                    "noc.services.escalator.maintenance.close_maintenance",
                    scheduler="escalator",
                    pool=self.escalate_managed_object.escalator_shard,
                    maintenance_id=self.id
                )

    def update_affected_objects(self):
        """
        Calculate and fill affected objects
        """
        def get_downlinks(objects):
            r = set()
            # Get all additional objects which may be affected
            for d in ObjectData._get_collection().find({
                "uplinks": {
                    "$in": list(objects)
                }
            }, {
                "_id": 1
            }):
                if d["_id"] not in objects:
                    r.add(d["_id"])
            if not r:
                return r
            # Leave only objects with all uplinks affected
            rr = set()
            for d in ObjectData._get_collection().find({
                "_id": {
                    "$in": list(r)
                }
            }, {
                "_id": 1,
                "uplinks": 1
            }):
                if len([1 for u in d["uplinks"] if u in objects]) == len(d["uplinks"]):
                    rr.add(d["_id"])
            return rr

        def get_segment_objects(segment):
            # Get objects belonging to segment
            so = set(
                ManagedObject.objects.filter(
                    segment=segment
                ).values_list("id", flat=True)
            )
            # Get objects from underlying segments
            for ns in NetworkSegment.objects.filter(parent=segment):
                so |= get_segment_objects(ns)
            return so

        # Calculate affected objects
        affected = set(o.object.id for o in self.direct_objects)
        for o in self.direct_segments:
            if o.segment:
                affected |= get_segment_objects(o.segment)
        while True:
            r = get_downlinks(affected)
            if not r:
                break
            affected |= r

        # @todo: Calculate affected objects considering topology
        affected = [{"object": o} for o in sorted(affected)]
        Maintainance._get_collection().update(
            {
                "_id": self.id
            },
            {
                "$set": {
                    "affected_objects": affected
                }
            }
        )

    @classmethod
    def currently_affected(cls):
        """
        Returns a list of currently affected object ids
        """
        affected = set()
        now = datetime.datetime.now()
        for d in cls._get_collection().find({
            "start": {
                "$lte": now
            },
            "is_completed": False
        }, {
            "_id": 0,
            "affected_objects": 1,
            "time_pattern": 1
        }):
            if d.get("time_pattern"):
                # Restrict to time pattern
                tp = TimePattern.get_by_id(d["time_pattern"])
                if tp and not tp.match(now):
                    continue
            affected.update([x["object"] for x in d["affected_objects"]])
        return list(affected)

    @classmethod
    def get_object_maintenance(cls, mo):
        """
        Returns a list of active maintenance for object
        :param mo: Managed Object instance
        :return: List of Maintainance instances or empty list
        """
        r = []
        now = datetime.datetime.now()
        for m in Maintainance.objects.filter(
                start__lte=now,
                is_completed=False,
                affected_objects__object=mo.id
        ).exclude("affected_objects").order_by("start"):
            if m.time_pattern and not m.time_pattern.match(now):
                continue
            r += [m]
        return r
