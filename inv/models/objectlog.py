<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ObjectLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectLog model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import (StringField, ObjectIdField, DateTimeField)


class ObjectLog(Document):
    meta = {
        "collection": "noc.objectlog",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["object"]
    }

    # Inventory object reference
    object = ObjectIdField()
    # Timestamp
    ts = DateTimeField()
    # Username
    user = StringField()
    # NOC subsystem
    system = StringField()
    # Managed object name
    managed_object = StringField()
    # Operation
    # * CREATE - Object created
    # * CHANGE - Object changed
    # * CONNECT - Object connected
    # * DISCONNECT - Object disconnected
    # * INSERT - Object moved into container
    # * REMOVE - Object removed from container
    op = StringField()
    # Message
    message = StringField()
