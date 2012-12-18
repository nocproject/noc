## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery id
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


class DiscoveryID(Document):
    """
    Managed Object's discovery identity
    """
    meta = {
        "collection": "noc.inv.discovery_id",
        "allow_inheritance": False,
        "indexes": ["object"]
    }
    object = ForeignKeyField(ManagedObject)
    first_chassis_mac = StringField()
    last_chassis_mac = StringField()
    hostname = StringField()
    router_id = StringField()

    def __unicode__(self):
        return self.object.name

    @classmethod
    def submit(cls, object, first_chassis_mac=None,
        last_chassis_mac=None, hostname=None, router_id=None):
        o = cls.objects.filter(object=object.id).first()
        if o:
            o.first_chassis_mac = first_chassis_mac
            o.last_chassis_mac = last_chassis_mac
            o.hostname = hostname
            o.router_id = router_id
            o.save()
        else:
            cls(object=object, first_chassis_mac=first_chassis_mac,
                last_chassis_mac=last_chassis_mac, hostname=hostname,
                router_id=router_id).save()
