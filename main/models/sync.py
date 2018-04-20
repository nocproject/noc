<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Sync document
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField)
# NOC Modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Sync document
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField)
## NOC Modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import ForeignKeyField
from noc.main.models import User


class Sync(Document):
    meta = {
        "collection": "noc.sync",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    user = ForeignKeyField(User)
    n_instances = IntField(default=1)

    def __unicode__(self):
        return self.name
