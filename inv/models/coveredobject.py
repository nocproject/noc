<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Covered Objects
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (IntField)
# NOC modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Covered Objects
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (IntField)
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from coverage import Coverage
from noc.inv.models.object import Object
from noc.lib.nosql import PlainReferenceField


class CoveredObject(Document):
    meta = {
        "collection": "noc.coveredobjects",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["coverage", "object"]
    }
    coverage = PlainReferenceField(Coverage)
    # Coverage preference.
    # The more is the better
    # Zero means coverage is explicitly disabled for ordering
    preference = IntField(default=100)

    object = PlainReferenceField(Object)

    def __unicode__(self):
        return u"%s %s" % (
            self.coverage.name,
            self.object.name or self.object.id
        )
