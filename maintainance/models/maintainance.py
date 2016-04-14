# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MaintainanceType
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, ReferenceField, DateTimeField, ListField, EmbeddedDocumentField
## NOC modules
from maintainancetype import MaintainanceType
from noc.sa.models.managedobject import ManagedObject
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_save
from noc.inv.models.objectuplink import ObjectUplink


class MaintainanceObject(EmbeddedDocument):
    object = ForeignKeyField(ManagedObject)


@on_save
class Maintainance(Document):
    meta = {
        "collection": "noc.maintainance",
        "indexes": [
            "affected_objects.object"
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
    # Objects declared to be affected my maintainance
    direct_objects = ListField(EmbeddedDocumentField(MaintainanceObject))
    # All objects affected by maintainance
    affected_objects = ListField(EmbeddedDocumentField(MaintainanceObject))
    # @todo: Attachments

    def on_save(self):
        self.update_affected_objects()

    def update_affected_objects(self):
        """
        Calculate and fill affected objects
        """
        # @todo:
        direct = set(o.object.id for o in self.direct_objects)
        # @todo: Calculate affected objects considering topology
        affected = [{"object": o} for o in sorted(direct)]
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
