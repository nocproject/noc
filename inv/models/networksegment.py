## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Segment
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, ReferenceField


class NetworkSegment(Document):
    meta = {
        "collection": "noc.networksegments",
        "indexes": ["parent"]
    }

    name = StringField(unique=True)
    parent = ReferenceField("self", required=False)
    description = StringField(required=False)
    settings = DictField(default=lambda: {}.copy())

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
