# ---------------------------------------------------------------------
# ObjectLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ObjectIdField, DateTimeField


class ObjectLog(Document):
    meta = {
        "collection": "noc.objectlog",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["object"],
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
    # * PARAM_CHANGED - Object param changed
    # * PARAM_RESET - Object param deleted
    op = StringField()
    # Message
    message = StringField()
