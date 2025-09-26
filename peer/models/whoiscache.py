# ----------------------------------------------------------------------
# WhoisCache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.validators import is_asn
from noc.core.ip import IP
from noc.core.prefixlist import optimize_prefix_list, optimize_prefix_list_maxlen
from noc.core.mongo.connection import get_db


class WhoisCache(object):
    """
    Whois cache interface
    """

    @classmethod
    def has_asset_members(cls):
        """
        Returns True if cache contains asset.members
        :return:
        """
        db = get_db()
        collection = db.noc.whois.asset.members
        return bool(collection.count_documents({}))

    @classmethod
    def has_origin_routes(cls):
        """
        Returns True if cache contains origin.routes
        :return:
        """
        db = get_db()
        collection = db.noc.whois.origin.route
        return bool(collection.count_documents({}))

    @classmethod
    def has_asset(cls, as_set):
        """
        Returns true if as-set has members in cache
        :param as_set:
        :return:
        """
        if is_asn(as_set[2:]):
            return True
        db = get_db()
        collection = db.noc.whois.asset.members
        return bool(collection.find_one({"_id": as_set}, {"_id": 1}))

    @classmethod
    def resolve_as_set(cls, as_set, seen=None, collection=None):
        members = set()
        if seen is None:
            seen = set()
        if collection is None:
            db = get_db()
            collection = db.noc.whois.asset.members
        for a in as_set.split():
            a = a.upper()
            seen.add(a)
            if is_asn(a[2:]):
                # ASN Given
                members.update([a.upper()])
            else:
                o = collection.find_one({"_id": a}, {"members": 1})
                if o:
                    for m in [x for x in o["members"] if x not in seen]:
                        members.update(cls.resolve_as_set(m, seen, collection))
        return members

    @classmethod
    def _resolve_as_set_prefixes(cls, as_set):
        db = get_db()
        collection = db.noc.whois.origin.route
        # Resolve
        prefixes = set()
        for a in cls.resolve_as_set(as_set):
            o = collection.find_one({"_id": a}, {"routes": 1})
            if o:
                prefixes.update(o["routes"])
        return prefixes

    @classmethod
    def resolve_as_set_prefixes(cls, as_set, optimize=None):
        prefixes = cls._resolve_as_set_prefixes(as_set)
        if optimize or (
            optimize is None
            and config.peer.prefix_list_optimization
            and len(prefixes) >= config.peer.prefix_list_optimization_threshold
        ):
            return set(optimize_prefix_list(prefixes))
        return prefixes

    @classmethod
    def resolve_as_set_prefixes_maxlen(cls, as_set, optimize=None):
        """
        Generate prefixes for as-sets.
        Returns a list of (prefix, min length, max length)
        """
        prefixes = cls._resolve_as_set_prefixes(as_set)
        max_len = config.peer.max_prefix_length
        if optimize or (
            optimize is None
            and config.peer.prefix_list_optimization
            and len(prefixes) >= config.peer.prefix_list_optimization_threshold
        ):
            # Optimization is enabled
            return [
                (p.prefix, p.mask, m)
                for p, m in optimize_prefix_list_maxlen(prefixes)
                if p.mask <= max_len
            ]
        # Optimization is disabled
        return [
            (x.prefix, x.mask, x.mask)
            for x in sorted([IP.prefix(p) for p in prefixes])
            if x.mask <= max_len
        ]

    @classmethod
    def cone_power(cls, as_set, mask):
        """
        Returns amount of prefixes of size _mask_ needed to cover as_set
        """
        n = 0
        for p in cls.resolve_as_set_prefixes(as_set, optimize=True):
            m = int(p.split("/")[1])
            if m <= mask:
                n += 2 * (mask - m)
        return n
