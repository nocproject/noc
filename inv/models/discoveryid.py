## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery id
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
from threading import Lock
## Third-party modules
from mongoengine.queryset import DoesNotExist
import cachetools
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ListField, LongField,
                                EmbeddedDocumentField)
from pymongo import ReadPreference
## NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.core.perf import metrics
from noc.core.cache.decorator import cachedmethod
from noc.core.cache.base import cache
from noc.core.mac import MAC

mac_lock = Lock()


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
        "indexes": [
            "object", "hostname", "udld_id", "macs"
        ]
    }
    object = ForeignKeyField(ManagedObject)
    chassis_mac = ListField(EmbeddedDocumentField(MACRange))
    hostname = StringField()
    router_id = StringField()
    udld_id = StringField()  # UDLD local identifier
    #
    macs = ListField(LongField())

    _mac_cache = cachetools.TTLCache(maxsize=10000, ttl=60)

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
            old_macs = set(m.first_mac for m in o.chassis_mac)
            o.chassis_mac = chassis_mac
            o.hostname = hostname
            o.router_id = router_id
            o.save()
            old_macs -= set(m.first_mac for m in o.chassis_mac)
            if old_macs:
                cache.delete_many(["discoveryid-mac-%s" % m for m in old_macs])
            # MAC index
            macs = []
            for r in chassis_mac:
                first = MAC(r.first_mac)
                last = MAC(r.last_mac)
                macs += [m for m in range(int(first), int(last) + 1)]
            o.macs = macs
        else:
            cls(object=object, chassis_mac=chassis_mac,
                hostname=hostname, router_id=router_id).save()

    @classmethod
    @cachedmethod(operator.attrgetter("_mac_cache"),
                  key="discoveryid-mac-%s",
                  lock=lambda _: mac_lock)
    def get_by_mac(cls, mac):
        return cls._get_collection().find_one({
            "macs": int(MAC(mac))
        }, {"_id": 0, "object": 1})

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
            metrics["discoveryid_mac_requests"] += 1
            r = cls.get_by_mac(mac)
            if r:
                return ManagedObject.get_by_id(r["object"])
            # Fallback to interface search
            metrics["discoveryid_mac_interface"] += 1
            o = set(
                d["managed_object"]
                for d in Interface._get_collection().find({
                    "mac": mac
                }, {
                    "_id": 0,
                    "managed_object": 1
                }, read_preference=ReadPreference.SECONDARY_PREFERRED)
            )
            if len(o) == 1:
                return ManagedObject.get_by_id(list(o)[0])
            metrics["discoveryid_mac_failed"] += 1
        if ipv4_address:
            metrics["discoveryid_ip_requests"] += 1
            # Try router_id
            d = DiscoveryID.objects.filter(router_id=ipv4_address).first()
            if d:
                metrics["discoveryid_ip_routerid"] += 1
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
                }, read_preference=ReadPreference.SECONDARY_PREFERRED)
                if has_ip(ipv4_address, d["ipv4_addresses"])
            )
            if len(o) == 1:
                metrics["discoveryid_ip_interface"] += 1
                return ManagedObject.get_by_id(list(o)[0])
            metrics["discoveryid_ip_failed"] += 1
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
