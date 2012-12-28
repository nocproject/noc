## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Pending Link Checks
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.nosql import (Document,
                           StringField, DateTimeField,
                           ForeignKeyField)
from noc.sa.models.managedobject import ManagedObject


class PendingLinkCheck(Document):
    """
    Customer MAC address changes
    """
    meta = {
        "collection": "noc.inv.pending_link_check",
        "allow_inheritance": False,
        "indexes": [("method", "local_object")]
    }
    method = StringField()
    local_object = ForeignKeyField(ManagedObject)
    local_interface = StringField()  # optional
    remote_object = ForeignKeyField(ManagedObject)
    remote_interface = StringField()
    expire = DateTimeField()

    def __unicode__(self):
        return u"%s:%s:%s:%s:%s" % (
            self.method, self.local_object.name, self.local_interface,
            self.remote_object.name, self.remote_interface)

    @classmethod
    def submit(cls, method, local_object, local_interface,
               remote_object, remote_interface):
        expire = datetime.datetime.now() + datetime.timedelta(days=2)
        plc = PendingLinkCheck.objects.filter(
            method=method,
            local_object=local_object.id,
            local_interface=local_interface,
            remote_object=remote_object.id,
            remote_interface=remote_interface
        ).first()
        if plc:
            plc.expire = expire
        else:
            plc = cls(
                method=method,
                local_object=local_object.id,
                local_interface=local_interface,
                remote_object=remote_object.id,
                remote_interface=remote_interface,
                expire=expire)
        plc.save()
