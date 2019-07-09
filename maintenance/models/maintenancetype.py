# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MaintenanceType
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


@six.python_2_unicode_compatible
class MaintenanceType(Document):
    meta = {
        "collection": "noc.maintenancetype",
        "strict": False,
        "auto_create_index": False,
        "legacy_collections": ["noc.maintainancetype"],
    }

    name = StringField(unique=True)
    description = StringField()
    suppress_alarms = BooleanField()
    card_template = StringField()

    def __str__(self):
        return self.name
