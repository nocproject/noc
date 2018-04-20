<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UnknownModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UnknownModel model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, URLField


class UnknownModel(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.unknown_models",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": [("vendor", "managed_object", "part_no")]
    }

    vendor = StringField()  # Vendor.code
    managed_object = StringField()  # ManagedObject.name
    platform = StringField()  # ManagedObject.platform
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
            "managed_object": managed_object.name,
<<<<<<< HEAD
            "platform": managed_object.platform.name if managed_object.platform else "",
=======
            "platform": managed_object.platform,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            "part_no": part_no
        }, update={
            # "$setOnInsert": {
            "$set": {
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
