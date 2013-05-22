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
from noc.lib.tt import tt_url
from noc.lib.rpsl import rpsl_format
from noc.lib.fields import INETField, TagsField
from noc.sa.profiles import profile_registry
from noc.main.models import NotificationGroup
from noc.lib.app.site import site
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


class WhoisASSetMembers(nosql.Document):
    """
    as-set -> members lookup
    """
    meta = {
        "collection": "noc.whois.asset.members",
        "allow_inheritance": False
    }

    as_set = nosql.StringField(unique=True)
    members = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.as_set

    @classmethod
    def lookup(cls, key):
        v = cls.objects.filter(as_set=key.upper()).first()
        if v is None:
            return []
        else:
            return v.members


class WhoisOriginRoute(nosql.Document):
    """
    origin -> route
    """
    meta = {
        "collection": "noc.whois.origin.route",
        "allow_inheritance": False
    }

    origin = nosql.StringField(unique=True)
    routes = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.as_set

    @classmethod
    def lookup(cls, key):
        v = cls.objects.filter(origin=key.upper()).first()
        if v is None:
            return []
        else:
            return v.routes


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
                o = collection.find_one({"as_set": a}, fields=["members"])
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
            o = collection.find_one({"origin": a}, fields=["routes"])
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


class PrefixListCachePrefix(nosql.EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    
    prefix = nosql.StringField(required=True)
    min = nosql.IntField(required=True)
    max = nosql.IntField(required=True)

    def __unicode__(self):
        return self.prefixes


class PrefixListCache(nosql.Document):
    """
    Prepared prefix-list cache. Can hold IPv4/IPv6 prefixes at same time.
    Prefixes are stored sorted
    """
    meta = {
        "collection": "noc.prefix_list_cache",
        "allow_inheritance": False
    }
    
    peering_point = nosql.ForeignKeyField(PeeringPoint)
    name = nosql.StringField()
    prefixes = nosql.ListField(nosql.EmbeddedDocumentField(PrefixListCachePrefix))
    changed = nosql.DateTimeField()
    pushed = nosql.DateTimeField()

    def __unicode__(self):
        return u" %s/%s" % (self.peering_point.hostname, self.name)

    def cmp_prefixes(self, prefixes):
        """
        Compare cached prefixes with a list of (prefix, min, max)
        """
        return [(c.prefix, c.min, c.max) for c in self.prefixes] == prefixes
