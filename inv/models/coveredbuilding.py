# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Covered Buildings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField

# NOC modules
from .coverage import Coverage
from noc.gis.models.building import Building
from noc.core.mongo.fields import PlainReferenceField


@six.python_2_unicode_compatible
class CoveredBuilding(Document):
    meta = {
        "collection": "noc.coveredbuildings",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["building", "coverage"],
    }
    coverage = PlainReferenceField(Coverage)
    # Coverage preference.
    # The more is the better
    # Zero means coverage is explicitly disabled for ordering
    preference = IntField(default=100)

    building = PlainReferenceField(Building)
    entrance = StringField(required=False)
    # Covered homes
    homes = IntField()

    def __str__(self):
        return "%s %s" % (self.coverage.name, self.building.primary_address.display_ru())
