# ---------------------------------------------------------------------
# Discovery id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import bisect
from threading import Lock
from typing import Optional, Union, Set

# Third-party modules
import bson
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, LongField, EmbeddedDocumentField
from pymongo import ReadPreference

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.change.decorator import change
from noc.config import config
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.core.perf import metrics
from noc.core.cache.decorator import cachedmethod
from noc.core.cache.base import cache
from noc.core.mac import MAC
from noc.core.model.decorator import on_delete

id_lock = Lock()
mac_lock = Lock()
IGNORED_CHASSIS_MACS = {MAC(m) for m in config.discovery.ignored_chassis_macs}


class MACRange(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    first_mac = StringField()
    last_mac = StringField()

    def __str__(self):
        return "%s - %s" % (self.first_mac, self.last_mac)


@change(audit=False)
@on_delete
class DiscoveryID(Document):
    """
    Managed Object's discovery identity
    """

    meta = {
        "collection": "noc.inv.discovery_id",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["object", "hostname", "hostname_id", "udld_id", "router_id", "macs"],
    }
    object = ForeignKeyField(ManagedObject)
    chassis_mac = ListField(EmbeddedDocumentField(MACRange))
    hostname = StringField()
    hostname_id = StringField()
    router_id = StringField()
    udld_id = StringField()  # UDLD local identifier
    #
    macs = ListField(LongField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _mac_cache = cachetools.TTLCache(maxsize=10000, ttl=60)
    _udld_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.object.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["DiscoveryID"]:
        return DiscoveryID.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            yield "managedobject", self.object.id

    @staticmethod
    def _macs_as_ints(ranges=None, additional=None, ignored_macs: Set[str] = None):
        """
        Get all MAC addresses within ranges as integers
        :param ranges: list of dicts {first_chassis_mac: ..., last_chassis_mac: ...}
        :param additional: Optional list of additional macs
        :return: List of integers
        """
        ranges = ranges or []
        additional = additional or []
        ignored_macs = ignored_macs or set()
        # Apply ranges
        macs = set()
        for r in ranges:
            if not r:
                continue
            first = MAC(r["first_chassis_mac"])
            last = MAC(r["last_chassis_mac"])
            if first in ignored_macs or last in ignored_macs:
                continue
            macs.update(m for m in range(int(first), int(last) + 1))
        # Append additional macs
        macs.update(int(MAC(m)) for m in additional if MAC(m) not in ignored_macs)
        return sorted(macs)

    @staticmethod
    def _macs_to_ranges(macs):
        """
        Convert list of macs (as integers) to MACRange
        :param macs: List of integer
        :return: List of MACRange
        """
        ranges = []
        for mi in macs:
            if ranges and mi - ranges[-1][1] == 1:
                # Extend last range
                ranges[-1][1] = mi
            else:
                # New range
                ranges += [[mi, mi]]
        return [MACRange(first_mac=str(MAC(r[0])), last_mac=str(MAC(r[1]))) for r in ranges]

    @classmethod
    def submit(cls, object, chassis_mac=None, hostname=None, router_id=None, additional_macs=None):
        # Process ranges
        macs = cls._macs_as_ints(chassis_mac, additional_macs, ignored_macs=IGNORED_CHASSIS_MACS)
        ranges = cls._macs_to_ranges(macs)
        # Update database
        o = cls.objects.filter(object=object.id).first()
        if o:
            old_macs = set(m.first_mac for m in o.chassis_mac)
            o.chassis_mac = ranges
            o.hostname = hostname
            o.hostname_id = hostname.lower() if hostname else None
            o.router_id = router_id
            old_macs -= set(m.first_mac for m in o.chassis_mac)
            if old_macs:
                cache.delete_many(["discoveryid-mac-%s" % m for m in old_macs])
            # MAC index
            o.macs = macs
            o.save()
        else:
            cls(
                object=object,
                chassis_mac=ranges,
                hostname=hostname,
                hostname_id=hostname.lower() if hostname else None,
                router_id=router_id,
                macs=macs,
            ).save()

    @classmethod
    @cachedmethod(
        operator.attrgetter("_mac_cache"), key="discoveryid-mac-%s", lock=lambda _: mac_lock
    )
    def get_by_mac(cls, mac):
        return cls._get_collection().find_one({"macs": int(MAC(mac))}, {"_id": 0, "object": 1})

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_udld_cache"), lock=lambda _: mac_lock)
    def get_by_udld_id(cls, device_id):
        return cls._get_collection().find_one({"udld_id": device_id}, {"_id": 0, "object": 1})

    @classmethod
    def find_object(
        cls, mac=None, ipv4_address=None, hostname: Optional[str] = None
    ) -> Optional[ManagedObject]:
        """
        Find managed object
        Args:
            mac:
            ipv4_address:
            cls:
        :return: Managed object instance or None
        """

        def has_ip(ip, addresses):
            x = ip + "/"
            for a in addresses:
                if a.startswith(x):
                    return True
            return False

        # Find by mac
        if mac:
            metrics["discoveryid_mac_requests"] += 1
            r = cls.get_by_mac(mac)
            if r:
                return ManagedObject.get_by_id(r["object"])
        if hostname:
            metrics["discoveryid_hostname_requests"] += 1
            d = DiscoveryID.objects.filter(hostname_id=hostname.lower()).first()
            if d:
                metrics["discoveryid_hostname"] += 1
                return d.object
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
                for d in SubInterface._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .find(
                    {"ipv4_addresses": {"$gt": ipv4_address + "/", "$lt": ipv4_address + "/99"}},
                    {"_id": 0, "managed_object": 1, "ipv4_addresses": 1},
                )
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
        # Get discovered chassis id range
        o = DiscoveryID.objects.filter(object=object.id).first()
        if o and o.chassis_mac:
            c_macs = [(r.first_mac, r.last_mac) for r in o.chassis_mac]
        else:
            c_macs = []
        # Get interface macs
        i_macs = set(
            i.mac
            for i in Interface.objects.filter(managed_object=object.id, mac__exists=True).only(
                "mac"
            )
            if i.mac
        )
        # Enrich discovered macs with additional interface's ones
        c_macs += [(m, m) for m in i_macs if not any(1 for f, t in c_macs if f <= m <= t)]
        return c_macs

    @classmethod
    def macs_for_objects(cls, objects_ids):
        """
        Get MAC addresses for object
        :param cls:
        :param objects_ids: Lis IDs of Managed Object Instance
        :type: list
        :return: Dictionary mac: objects
        :rtype: dict
        """
        if not objects_ids:
            return None
        if isinstance(objects_ids, list):
            objects = objects_ids
        else:
            objects = list(objects_ids)

        os = cls.objects.filter(object__in=objects)
        if not os:
            return None
        # Discovered chassis id range
        c_macs = {int(did[0][0]): did[1] for did in os.scalar("macs", "object") if did[0]}
        # c_macs = [r.macs for r in os]
        # Other interface macs
        i_macs = {
            int(MAC(i[0])): i[1]
            for i in Interface.objects.filter(managed_object__in=objects, mac__exists=True).scalar(
                "mac", "managed_object"
            )
            if i[0]
        }
        # Other subinterface macs (actual for DSLAM)
        si_macs = {
            int(MAC(i[0])): i[1]
            for i in SubInterface.objects.filter(
                managed_object__in=objects, mac__exists=True
            ).scalar("mac", "managed_object")
            if i[0]
        }
        c_macs.update(i_macs)
        c_macs.update(si_macs)

        return c_macs

    def on_delete(self):
        # Reset cache
        macs = set(m.first_mac for m in self.chassis_mac)
        if macs:
            cache.delete_many(["discoveryid-mac-%s" % m for m in macs])

    @classmethod
    def clean_for_object(cls, mo):
        if hasattr(mo, "id"):
            mo = mo.id
        for d in DiscoveryID.objects.filter(object=mo):
            d.delete()

    @classmethod
    def find_objects(cls, macs):
        """
        Find objects for list of macs
        :param macs: List of MAC addresses
        :return: dict of MAC -> ManagedObject for resolved MACs
        """
        r = {}
        if not macs:
            return r
        # Build list of macs to search
        mlist = sorted(int(MAC(m)) for m in macs)
        # Search for macs
        obj_ranges = {}  # (first, last) -> mo
        for d in DiscoveryID._get_collection().find(
            {"macs": {"$in": mlist}}, {"_id": 0, "object": 1, "chassis_mac": 1}
        ):
            mo = ManagedObject.get_by_id(d["object"])
            if mo:
                for dd in d.get("chassis_mac", []):
                    obj_ranges[int(MAC(dd["first_mac"])), int(MAC(dd["last_mac"]))] = mo
        n = 1
        for s, e in obj_ranges:
            n += 1
        # Resolve ranges
        start = 0
        ll = len(mlist)
        for s, e in sorted(obj_ranges):
            mo = obj_ranges[s, e]
            start = bisect.bisect_left(mlist, s, start, ll)
            while start < ll and s <= mlist[start] <= e:
                r[MAC(mlist[start])] = mo
                start += 1
        return r

    @classmethod
    def find_all_objects(cls, mac):
        """
        Find objects for mac
        :return: dict of ManagedObjects ID for resolved MAC
        """
        r = []
        if not mac:
            return r
        metrics["discoveryid_mac_requests"] += 1
        for d in DiscoveryID._get_collection().find(
            {"macs": int(MAC(mac))}, {"_id": 0, "object": 1, "chassis_mac": 1}
        ):
            mo = ManagedObject.get_by_id(d["object"])
            if mo:
                r.append(mo.id)
        return r

    @classmethod
    def update_udld_id(cls, object, local_id):
        """
        Update UDLD id if necessary
        :param object: Object for set
        :param local_id: Local UDLD id
        :return:
        """
        DiscoveryID._get_collection().update_one(
            {"object": object.id}, {"$set": {"udld_id": local_id}}, upsert=True
        )
