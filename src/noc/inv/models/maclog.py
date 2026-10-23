# ---------------------------------------------------------------------
# MAC Database History
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField, IntField


class MACLog(Document):
    """
    Customer MAC address changes
    """

    meta = {
        "collection": "noc.mac_log",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["mac", "-timestamp"],
    }
    # Todo: Add Validation
    timestamp = DateTimeField()
    mac = StringField()
    vc_domain_name = StringField()
    vlan = IntField()
    managed_object_name = StringField()
    interface_name = StringField()
