## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Segment
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, DictField, ReferenceField,
                                ListField)
from noc.lib.nosql import ForeignKeyField
from noc.sa.models.managedobjectselector import ManagedObjectSelector


class NetworkSegment(Document):
    meta = {
        "collection": "noc.networksegments",
        "indexes": ["parent", "sibling"]
    }

    name = StringField(unique=True)
    parent = ReferenceField("self", required=False)
    description = StringField(required=False)
    settings = DictField(default=lambda: {}.copy())
    tags = ListField(StringField())
    # Selectors for fake segments
    # Transition only, should not be used
    selector = ForeignKeyField(ManagedObjectSelector)
    # Sibling segment, if part of larger structure with
    # horizontal links
    sibling = ReferenceField("self")

    def __unicode__(self):
        return self.name

    @property
    def effective_settings(self):
        """
        Returns dict with effective settings
        """
        if hasattr(self, "_es"):
            return self._es
        # Build full parent stack
        sstack = [self.settings or {}]
        p = self.parent
        while p:
            sstack = [p.settings or {}] + sstack
            p = p.parent
        # Get effective settings
        es = {}
        for s in sstack:
            for k in s:
                v = s[k]
                if v:
                    # Override parent settings
                    es[k] = v
                elif k in es:
                    # Ignore parent settings
                    del es[k]
        self._es = es
        return es

    @property
    def has_loop(self):
        """
        Check if object creates loop
        """
        if not self.id:
            return False
        p = self.parent
        while p:
            if p.id == self.id:
                return True
            p = p.parent
        return False

    @property
    def managed_objects(self):
        from noc.sa.models.managedobject import ManagedObject

        if self.selector:
            return self.selector.managed_objects
        else:
            siblings = self.get_siblings()
            if len(siblings) == 1:
                q = {"segment": str(siblings.pop().id)}
            else:
                q = {"segment__in": [str(s.id) for s in siblings]}
            return ManagedObject.objects.filter(**q)

    def get_siblings(self, seen=None):
        seen = seen or set()
        ss = set([self])
        seen |= ss
        if self.sibling and self.sibling not in seen:
            ss |= self.sibling.get_siblings(seen)
        seen |= ss
        for s in NetworkSegment.objects.filter(sibling=self):
            ss |= s.get_siblings(seen)
        return ss
