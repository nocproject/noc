# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectPath
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import ListField, ObjectIdField, IntField
## NOC modules
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object


class ObjectPath(Document):
    meta = {
        "collection": "noc.cache.objectpaths",
        "allow_inheritance": False,
    }
    # Object id
    object = IntField(primary_key=True)
    adm_path = ListField(IntField())
    segment_path = ListField(ObjectIdField())
    container_path = ListField(ObjectIdField())

    @classmethod
    def refresh(cls, obj):
        ObjectPath._get_collection().update(
            {
                "_id": obj.id
            },
            {
                "$set": {
                    "adm_path": obj.administrative_domain.get_path(),
                    "segment_path": obj.segment.get_path(),
                    "container_path": obj.container.get_path() if obj.container else []
                }
            },
            upsert=True
        )

    @classmethod
    def get_path(cls, object):
        return ObjectPath.objects.filter(object=object.id).first()
