## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.queryset import DoesNotExist
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ListField,
                                EmbeddedDocumentField)
## NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface


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
    def find_object(cls, mac=None, ipv4_address=None):
        """
        Find managed object
        :param cls:
        :return: Managed object instance or None
        """
        def has_ip(ip, addresses):
            x = ip + "/"
            for a in addresses:
                if a.startswith(x):
                    return True
            return False

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
                return ManagedObject.get_by_id(r["object"])
            # Fallback to interface search
            o = set(
                d["managed_object"]
                for d in Interface._get_collection().find({
                    "mac": mac
                }, {
                    "_id": 0,
                    "managed_object": 1
                })
            )
            if len(o) == 1:
                return ManagedObject.get_by_id(list(o)[0])
        if ipv4_address:
            # Try router_id
            d = DiscoveryID.objects.filter(router_id=ipv4_address).first()
            if d:
                return d.object
            # Fallback to interface addresses
            o = set(
                d["managed_object"]
                for d in SubInterface._get_collection().find({
                    "ipv4_addresses": {
                        "$gt": ipv4_address + "/",
                        "$lt": ipv4_address + "/99"
                    }
                }, {
                    "_id": 0,
                    "managed_object": 1,
                    "ipv4_addresses": 1
                })
                if has_ip(ipv4_address, d["ipv4_addresses"])
            )
            if len(o) == 1:
                return ManagedObject.get_by_id(list(o)[0])
        return None

    @classmethod
    def macs_for_object(cls, object):
        """
        Get MAC addresses for object
        :param cls:
        :param object:
        :return: list of (fist_mac, last_mac)
        """
        try:
            o = cls.objects.get(object=object.id)
        except DoesNotExist:
            return []
        if not o or not o.chassis_mac:
            return None
        # Discovered chassis id range
        c_macs = [(r.first_mac, r.last_mac) for r in o.chassis_mac]
        # Other interface macs
        i_macs = set()
        for i in Interface.objects.filter(
                managed_object=object.id, mac__exists=False):
            if i.mac:
                if not any(1 for f, t in c_macs if f <= i.mac <= t):
                    # Not in range
                    i_macs.add(i.mac)
        return c_macs + [(m, m) for m in i_macs]
