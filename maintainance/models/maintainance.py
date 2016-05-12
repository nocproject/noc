# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Maintainance
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python
import datetime
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, BooleanField, ReferenceField, DateTimeField,
    ListField, EmbeddedDocumentField
)
## NOC modules
from maintainancetype import MaintainanceType
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_save
from noc.inv.models.objectuplink import ObjectUplink


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
    # Objects declared to be affected by maintainance
    direct_objects = ListField(EmbeddedDocumentField(MaintainanceObject))
    # Segments declared to be affected by maintainance
    direct_segments = ListField(EmbeddedDocumentField(MaintainanceSegment))
    # All objects affected by maintainance
    affected_objects = ListField(EmbeddedDocumentField(MaintainanceObject))
    # @todo: Attachments

    def on_save(self):
        self.update_affected_objects()

    def update_affected_objects(self):
        """
        Calculate and fill affected objects
        """
        def get_downlinks(objects):
            r = set()
            # Get all additional objects which may be affected
            for d in ObjectUplink._get_collection().find({
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
            for d in ObjectUplink._get_collection().find({
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
        }):
            affected.update([x["object"] for x in d["affected_objects"]])
        return list(affected)
