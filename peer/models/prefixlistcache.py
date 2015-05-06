# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Peer module models
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, IntField,
                                ListField, EmbeddedDocumentField, DateTimeField)
## NOC modules
from peeringpoint import PeeringPoint
from noc.lib.nosql import ForeignKeyField


class PrefixListCachePrefix(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    
    prefix = StringField(required=True)
    min = IntField(required=True)
    max = IntField(required=True)

    def __unicode__(self):
        return self.prefix


class PrefixListCache(Document):
    """
    Prepared prefix-list cache. Can hold IPv4/IPv6 prefixes at same time.
    Prefixes are stored sorted
    """
    meta = {
        "collection": "noc.prefix_list_cache",
        "allow_inheritance": False
    }
    
    peering_point = ForeignKeyField(PeeringPoint)
    name = StringField()
    prefixes = ListField(EmbeddedDocumentField(PrefixListCachePrefix))
    changed = DateTimeField()
    pushed = DateTimeField()

    def __unicode__(self):
        return u" %s/%s" % (self.peering_point.hostname, self.name)

    def cmp_prefixes(self, prefixes):
        """
        Compare cached prefixes with a list of (prefix, min, max)
        """
        return [(c.prefix, c.min, c.max) for c in self.prefixes] == prefixes
