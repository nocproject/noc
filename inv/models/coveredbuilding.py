<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Covered Buildings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, IntField)
# NOC modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Covered Buildings
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, IntField)
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from coverage import Coverage
from noc.gis.models.building import Building
from noc.lib.nosql import PlainReferenceField


class CoveredBuilding(Document):
    meta = {
        "collection": "noc.coveredbuildings",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["building", "coverage"]
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

    def __unicode__(self):
        return u"%s %s" % (
            self.coverage.name,
            self.building.primary_address.display_ru()
        )
