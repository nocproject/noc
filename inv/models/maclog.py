<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MAC Database History
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MAC Database History
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import (Document, StringField, DateTimeField,
                           IntField)


class MACLog(Document):
    """
    Customer MAC address changes
    """
    meta = {
        "collection": "noc.mac_log",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        "indexes": ["mac", "-timestamp"]
    }
    # Todo: Add Validation
    timestamp = DateTimeField()
    mac = StringField()
    vc_domain_name = StringField()
    vlan = IntField()
    managed_object_name = StringField()
    interface_name = StringField()
