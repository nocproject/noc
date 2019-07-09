# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UnknownModel model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField


@six.python_2_unicode_compatible
class UnknownModel(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.unknown_models",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("vendor", "managed_object", "part_no")],
    }

    vendor = StringField()  # Vendor.code
    managed_object = StringField()  # ManagedObject.name
    platform = StringField()  # ManagedObject.platform
    part_no = StringField()
    description = StringField()

    def __str__(self):
        return "%s, %s, %s" % (self.vendor, self.managed_object, self.part_no)

    @classmethod
    def mark_unknown(cls, vendor, managed_object, part_no, description=""):
        cls._get_collection().find_and_modify(
            {
                "vendor": vendor,
                "managed_object": managed_object.name,
                "platform": managed_object.platform.name if managed_object.platform else "",
                "part_no": part_no,
            },
            update={
                # "$setOnInsert": {
                "$set": {"description": description}
            },
            upsert=True,
        )

    @classmethod
    def clear_unknown(cls, vendor, part_numbers):
        cls._get_collection().delete_many({"vendor": vendor, "part_no": {"$in": part_numbers}})
