# ---------------------------------------------------------------------
# Discovery id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import bisect
from threading import Lock
from typing import Optional, Union, Iterable, List, Set

# Third-party modules
import bson
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, ListField, LongField, EmbeddedDocumentField
from pymongo import ReadPreference, ReturnDocument

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.change.decorator import change
from noc.config import config
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.macblacklist import MACBlacklist
from noc.core.perf import metrics
from noc.core.cache.base import cache
from noc.core.mac import MAC
from noc.core.model.decorator import on_delete

id_lock = Lock()
mac_lock = Lock()


class MACRange(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    first_mac = StringField()
    last_mac = StringField()

    def __str__(self) -> str:
        if self.first_mac == self.last_mac:
            return self.first_mac
        return f"{self.first_mac} - {self.last_mac}"

    @classmethod
    def from_str(cls, first: str, last: str) -> "MACRange":
        """
        Create MACRange from two macs.

        Rearrange when necessary.

        Args:
            first: First MAC.
            last: Last MAC.

        Returns:
            New MACRange instance.
        """
        if first > last:
            first, last = last, first
        return MACRange(first_mac=str(MAC(first)), last_mac=str(MAC(last)))

    def iter_as_int(self) -> Iterable[int]:
        """Iterate all MACs in range as integers."""
        return range(int(MAC(self.first_mac)), int(MAC(self.last_mac)) + 1)


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
    object = ForeignKeyField(ManagedObject, unique=True)
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
    def _macs_as_ints(
        ranges: Optional[List[MACRange]] = None, additional: Optional[Iterable[str]] = None
    ) -> List[int]:
        """
        Get all MAC addresses within ranges as integers.

        Args:
            ranges: List of MACRange
            additionals: Additional MAC Addresses

        Returns:
            List of MACs in integer form
        """
        # Resulting set
        macs: Set[int]
        if additional:
            macs = {int(MAC(mac)) for mac in additional}
        else:
            macs = set()
        # Process ranges
        if ranges:
            for r in ranges:
                macs.update(r.iter_as_int())
        return sorted(macs)

    @staticmethod
    def _macs_to_ranges(macs: Iterable[int]) -> Iterable[MACRange]:
        """
        Compact MAC addresses to ranges.

        Args:
            macs: MAC addresses in integer form.

        Returns:
            Yields MACRanges
        """
        first: Optional[int] = None
        last: Optional[int] = None
        for mac in macs:
            if MACBlacklist.is_banned_mac(mac, is_ignored=True):
                continue
            if last is None:
                # First range
                first = mac
                last = mac
            elif mac - last == 1:
                # Continue range
                last += 1
            else:
                # Range stopped
                yield MACRange(first_mac=str(MAC(first)), last_mac=str(MAC(last)))
                first = None
                last = None
        if last is not None:
            yield MACRange(first_mac=str(MAC(first)), last_mac=str(MAC(last)))

    @classmethod
    def submit(
        cls,
        object: ManagedObject,
        chassis_mac: Optional[List[MACRange]] = None,
        hostname: Optional[str] = None,
        router_id: Optional[str] = None,
        additional_macs: Optional[Iterable[str]] = None,
    ):
        # Process ranges
        macs = cls._macs_as_ints(chassis_mac, additional_macs)
        ranges = list(cls._macs_to_ranges(macs))
        # Perform one-shot atomic upsert
        # to protect against race conditions
        result = cls._get_collection().find_one_and_update(
            {"object": object.id},
            {
                "$set": {
                    "chassis_mac": [mr.to_mongo() for mr in ranges],
                    "hostname": hostname,
                    "hostname_id": hostname.lower() if hostname else None,
                    "router_id": router_id,
                    "macs": macs,
                }
            },
            upsert=True,
            return_document=ReturnDocument.BEFORE,
        )
        if result is None and macs:
            # Not seen before, invalidate all macs
            cache.delete_many([f"discovery-id-{m}" for m in macs])
        elif result is not None and macs:
            # Invalidate dereferenced macs
            old_macs: Optional[List[int]] = result.get("macs")
            if old_macs and old_macs != macs:
                cache.delete_many([f"discovery-id-{m}" for m in set(old_macs) - set(macs)])

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_udld_cache"), lock=lambda _: mac_lock)
    def get_by_udld_id(cls, device_id):
        return cls._get_collection().find_one({"udld_id": device_id}, {"_id": 0, "object": 1})

    @classmethod
    def find_object_by_mac(cls, mac: str) -> Optional[ManagedObject]:
        """
        Find Managed Object by MAC.

        Args:
            mac: MAC Address.

        Returns:
            ManagedObject instance, if found. None otherwise.
        """
        metrics["discoveryid_mac_requests"] += 1
        # This method has high miss rate so we cannot use @cachedmethod
        mi = int(str(MAC))
        r = cache.get(f"discovery-id-{mi}")
        if r is not None:
            metrics["discoveryid_mac_hits"] += 1
            return ManagedObject.get_by_id(r)  # cached
        # Lookup database
        r = cls._get_collection().find_one({"macs": mi}, {"_id": 0, "object": 1})
        if not r:
            return None  # miss
        # Dereference
        obj = ManagedObject.get_by_id(r["object"])
        if obj is None:
            return None  # dereference failed
        cache.set(f"discovery-id-{mi}", obj.id)
        return obj

    @classmethod
    def find_object_by_hostname(cls, hostname: str) -> Optional[ManagedObject]:
        """
        Find object by hostname.

        Args:
            hostname: Host name.

        Returns:
            Managed Object instance, if found, None otherwise.
        """
        metrics["discoveryid_hostname_requests"] += 1
        r = cls._get_collection().find_one(
            {"hostname_id": hostname.lower()}, {"_id": 0, "object": 1}
        )
        if r is None:
            return None
        return ManagedObject.get_by_id(r["object"])

    @classmethod
    def find_object_by_ip(cls, address: str) -> Optional[ManagedObject]:
        """
        Find object by ipv4_address.

        Args:
            address: IP address.

        Returns:
            Managed Object instance, if found. None otherwise.
        """

        def has_ip(ip: str, addresses: list[str]) -> bool:
            x = ip + "/"
            for a in addresses:
                if a.startswith(x):
                    return True
            return False

        metrics["discoveryid_ip_requests"] += 1
        # Try router id
        r = cls._get_collection().find_one({"router_id": address}, {"_id": 0, "object": 1})
        if r:
            mo = ManagedObject.get_by_id(r["object"])
            if mo:
                return mo
        # Fallback to interface addresses
        o = set(
            d["managed_object"]
            for d in SubInterface._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find(
                {"ipv4_addresses": {"$gt": address + "/", "$lt": address + "/99"}},
                {"_id": 0, "managed_object": 1, "ipv4_addresses": 1},
            )
            if has_ip(address, d["ipv4_addresses"])
        )
        if len(o) != 1:
            return None
        return ManagedObject.get_by_id(list(o)[0])

    @classmethod
    def find_object(
        cls,
        mac: Optional[str] = None,
        ipv4_address: Optional[str] = None,
        hostname: Optional[str] = None,
    ) -> Optional[ManagedObject]:
        """
        Find managed object.
        Args:
            mac: MAC Address
            ipv4_address: IPv4 Address
            hostname: Hostname

        Returns:
            Managed object instance or None
        """

        # Find by mac
        if mac:
            r = cls.find_object_by_mac(mac)
            if r:
                return r
        if hostname:
            r = cls.find_object_by_hostname(hostname)
            if r:
                return r
        if ipv4_address:
            r = cls.find_object_by_ip(ipv4_address)
            if r:
                return r
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
