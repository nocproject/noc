# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## StaticRoute fact
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class StaticRoute(BaseFact):
    ATTRS = ["prefix", "afi", "vrf", "interface", "next_hop",
             "description", "tag", "distance", "discard"]
    ID = ["vrf", "prefix", "next_hop"]

    def __init__(self, prefix, afi=None, vrf=None, interface=None,
                 next_hop=None, description=None, tag=None,
                 distance=None, discard=None):
        super(StaticRoute, self).__init__()
        self.prefix = prefix
        self.afi = afi
        self.vrf = vrf
        self.interface = interface
        self.next_hop = next_hop
        self.description = description
        self.tag = tag
        self.distance = distance
        self.discard = discard

    def __unicode__(self):
        if self.vrf:
            return "StaticRoute %s:%s" % (self.vrf, self.prefix)
        else:
            return "StaticRoute %s" % self.prefix

    @property
    def prefix(self):
        return self._prefix
    
    @prefix.setter
    def prefix(self, value):
        self._prefix = value or None
        if ":" in value:
            self.afi = "IPv6"
        else:
            self.afi = "IPv4"

    @property
    def afi(self):
        return self._afi
    
    @afi.setter
    def afi(self, value):
        if value is None and self.prefix:
            return
        self._afi = value or None

    @property
    def vrf(self):
        return self._vrf
    
    @vrf.setter
    def vrf(self, value):
        self._vrf = value or None

    @property
    def interface(self):
        return self._interface
    
    @interface.setter
    def interface(self, value):
        self._interface = value or None

    @property
    def next_hop(self):
        return self._next_hop
    
    @next_hop.setter
    def next_hop(self, value):
        self._next_hop = value or None

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value or None

    @property
    def tag(self):
        return self._tag
    
    @tag.setter
    def tag(self, value):
        self._tag = int(value) if value is not None else None

    @property
    def distance(self):
        return self._distance
    
    @distance.setter
    def distance(self, value):
        self._distance = int(value) if value is not None else None

    @property
    def discard(self):
        return self._discard
    
    @discard.setter
    def discard(self, value):
        self._discard = bool(value) if value is not None else None
