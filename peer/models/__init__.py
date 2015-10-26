# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer module models
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models, connection
## NOC modules
from noc.settings import config
from noc.lib.validators import is_asn
from noc.lib.ip import IP
from noc.peer.tree import optimize_prefix_list, optimize_prefix_list_maxlen
from noc.lib import nosql

from rir import RIR
from person import Person
from maintainer import Maintainer
from organisation import Organisation
from asn import AS


class CommunityType(models.Model):
    class Meta:
        verbose_name = "Community Type"
        verbose_name_plural = "Community Types"

    name = models.CharField("Description", max_length=32, unique=True)

    def __unicode__(self):
        return self.name


class Community(models.Model):
    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"

    community = models.CharField("Community", max_length=20, unique=True)
    type = models.ForeignKey(CommunityType, verbose_name="Type")
    description = models.CharField("Description", max_length=64)

    def __unicode__(self):
        return self.community

from asset import ASSet
from peeringpoint import PeeringPoint
from peergroup import PeerGroup
from peer import Peer
from whoisassetmembers import WhoisASSetMembers
from whoisoriginroute import WhoisOriginRoute


class WhoisCache(object):
    """
    Whois cache interface
    """
    @classmethod
    def resolve_as_set(cls, as_set, seen=None, collection=None):
        members = set()
        if seen is None:
            seen = set()
        if collection is None:
            db = nosql.get_db()
            collection = db.noc.whois.asset.members
        for a in as_set.split():
            a = a.upper()
            seen.add(a)
            if is_asn(a[2:]):
                # ASN Given
                members.update([a.upper()])
            else:
                o = collection.find_one({"_id": a}, fields=["members"])
                if o:
                    for m in [x for x in o["members"] if x not in seen]:
                        members.update(cls.resolve_as_set(m, seen, collection))
        return members

    @classmethod
    def _resolve_as_set_prefixes(cls, as_set):
        db = nosql.get_db()
        collection = db.noc.whois.origin.route
        # Resolve
        prefixes = set()
        for a in cls.resolve_as_set(as_set):
            o = collection.find_one({"_id": a}, fields=["routes"])
            if o:
                prefixes.update(o["routes"])
        return prefixes

    @classmethod
    def resolve_as_set_prefixes(cls, as_set, optimize=None):
        prefixes = cls._resolve_as_set_prefixes(as_set)
        pl_optimize = config.getboolean("peer", "prefix_list_optimization")
        threshold = config.getint("peer", "prefix_list_optimization_threshold")
        if (optimize or
            (optimize is None and pl_optimize and len(prefixes) >= threshold)):
            return set(optimize_prefix_list(prefixes))
        return prefixes

    @classmethod
    def resolve_as_set_prefixes_maxlen(cls, as_set, optimize=None):
        """
        Generate prefixes for as-sets.
        Returns a list of (prefix, min length, max length)
        """
        prefixes = cls._resolve_as_set_prefixes(as_set)
        pl_optimize = config.getboolean("peer", "prefix_list_optimization")
        threshold = config.getint("peer", "prefix_list_optimization_threshold")
        max_len = config.getint("peer", "max_prefix_length")
        if (optimize or
            (optimize is None and pl_optimize and len(prefixes) >= threshold)):
            # Optimization is enabled
            return [(p.prefix, p.mask, m) for p, m
                in optimize_prefix_list_maxlen(prefixes)
                if p.mask <= max_len]
        else:
            # Optimization is disabled
            return [(x.prefix, x.mask, x.mask)
                for x in sorted([IP.prefix(p) for p in prefixes])
                if x.mask <= max_len]

    @classmethod
    def cone_power(cls, as_set, mask):
        """
        Returns amount of prefixes of size _mask_ needed to cover as_set
        """
        n = 0
        for p in cls.resolve_as_set_prefixes(as_set, optimize=True):
            m = int(p.split("/")[1])
            if m <= mask:
                n += long(2 * (mask - m))
        return n

from prefixlistcache import PrefixListCache, PrefixListCachePrefix