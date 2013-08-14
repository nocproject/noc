## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, EmbeddedDocument,
                           StringField, ListField,
                           ForeignKeyField, EmbeddedDocumentField)
from noc.sa.models.managedobject import ManagedObject


class MACRange(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    first_mac = StringField()
    last_mac = StringField()

    def __unicode__(self):
        return u"%s - %s" % (self.first_mac, self.last_mac)


class DiscoveryID(Document):
    """
    Managed Object's discovery identity
    """
    meta = {
        "collection": "noc.inv.discovery_id",
        "allow_inheritance": False,
        "indexes": ["object", "hostname", "udld_id"]
    }
    object = ForeignKeyField(ManagedObject)
    chassis_mac = ListField(EmbeddedDocumentField(MACRange))
    hostname = StringField()
    router_id = StringField()
    udld_id = StringField()  # UDLD local identifier

    def __unicode__(self):
        return self.object.name

    @classmethod
    def submit(cls, object, chassis_mac=None,
               hostname=None, router_id=None):
        if chassis_mac:
            chassis_mac = [
                MACRange(
                    first_mac=r["first_chassis_mac"],
                    last_mac=r["last_chassis_mac"]
                ) for r in chassis_mac
            ]
        o = cls.objects.filter(object=object.id).first()
        if o:
            o.chassis_mac = chassis_mac
            o.hostname = hostname
            o.router_id = router_id
            o.save()
        else:
            cls(object=object, chassis_mac=chassis_mac,
                hostname=hostname, router_id=router_id).save()

    @classmethod
    def find_object(cls, mac=None):
        """
        Find managed object
        :param cls:
        :return: Managed object instance or None
        """
        c = cls._get_collection()
        # Find by mac
        if mac:
            r = c.find_one({
                "chassis_mac": {
                    "$elemMatch": {
                        "first_mac": {
                            "$lte": mac
                        },
                        "last_mac": {
                            "$gte": mac
                        }
                    }
                }
            })
            if r:
                return ManagedObject.objects.get(id=r["object"])
        return None
