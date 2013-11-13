## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UnknownModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, URLField


class UnknownModel(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.unknown_model",
        "allow_inheritance": False,
        "indexes": [("vendor", "managed_object", "part_no")]
    }

    vendor = StringField()  # Vendor.code
    managed_object = StringField()  # ManagedObject.name
    part_no = StringField()
    description = StringField()

    def __unicode__(self):
        return u"%s, %s, %s" % (
            self.vendor, self.managed_object, self.part_no)

    @classmethod
    def mark_unknown(cls, vendor, managed_object, part_no,
                     description=""):
        cls._get_collection().find_and_modify({
            "vendor": vendor,
            "managed_object": managed_object,
            "part_no": part_no
        }, update={
            "$setOnInsert": {
                "description": description
            }
        }, upsert=True)

    @classmethod
    def clear_unknown(cls, vendor, part_numbers):
        cls._get_collection().remove({
            "vendor": vendor,
            "part_no": {
                "$in": part_numbers
            }
        })
