# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RR helper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.comp import smart_text

TYPE_PREF = {"NS": 0, "MX": 10}
DEFAULT_PREF = 100


class RR(object):
    __slots__ = [
        "zone",
        "name",
        "ttl",
        "type",
        "priority",
        "rdata",
        "_idna",
        "_content",
        "_order",
        "_sorder",
    ]

    def __init__(self, zone, name, ttl, type, rdata, priority=None):
        self.zone = zone
        self.name = name
        self.ttl = ttl
        self.type = type
        self.rdata = rdata
        self.priority = priority
        if name.endswith("."):
            self._idna = self.to_idna(name)
        elif name:
            self._idna = self.to_idna("%s.%s." % (name, zone))
        else:
            self._idna = self.to_idna("%s." % zone)
        if type in ("NS", "MX", "CNAME"):
            self._content = self.to_idna(rdata)
        else:
            self._content = rdata
        if type == "PTR":
            self._order = tuple(self.maybe_int(x) for x in name.split("."))
        l_suffix = len(self.to_idna(zone)) + 1
        self._sorder = self._idna[:-l_suffix]

    def __repr__(self):
        return "<RR %s %s %s>" % (self.name, self.type, self.rdata)

    def __lt__(self, other):
        # Check type preferences
        p1 = TYPE_PREF.get(self.type, DEFAULT_PREF)
        p2 = TYPE_PREF.get(other.type, DEFAULT_PREF)
        if p1 != p2:
            return p1 < p2
        # Compare PTR
        if self.type == "PTR" and other.type == "PTR":
            return self._order < other._order
        # Compare by name
        if self._sorder < other._sorder:
            return True
        elif self._sorder > other._sorder:
            return False
        # Compare by type
        if self.type < other.type:
            return True
        elif self.type > other.type:
            return False
        # Compare by content
        if self._content < other._content:
            return True
        elif self._content > other._content:
            return False
        # Compare by TTL
        if self.ttl < other.ttl:
            return True
        elif self.ttl > other.ttl:
            return False
        # Compare by priority
        return self.priority < other.priority

    def to_json(self):
        r = {"name": self.name, "type": self.type, "rdata": self.rdata}
        if self.ttl:
            r["ttl"] = self.ttl
        if self.priority:
            r["priority"] = self.priority
        return r

    @staticmethod
    def to_idna(n):
        if isinstance(n, unicode):
            return n.lower().encode("idna")
        elif isinstance(n, str):
            return smart_text(n, "utf-8").lower().encode("idna")
        return n

    @staticmethod
    def maybe_int(v):
        try:
            return int(v)
        except ValueError:
            return v
