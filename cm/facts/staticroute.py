# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# StaticRoute fact
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## StaticRoute fact
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @afi.setter
    def afi(self, value):
        if value is None and self.prefix:
            return
        self._afi = value or None

    @property
    def vrf(self):
        return self._vrf
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @vrf.setter
    def vrf(self, value):
        self._vrf = value or None

    @property
    def interface(self):
        return self._interface
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @interface.setter
    def interface(self, value):
        self._interface = value or None

    @property
    def next_hop(self):
        return self._next_hop
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @next_hop.setter
    def next_hop(self, value):
        self._next_hop = value or None

    @property
    def description(self):
        return self._description
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @description.setter
    def description(self, value):
        self._description = value or None

    @property
    def tag(self):
        return self._tag
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @tag.setter
    def tag(self, value):
        self._tag = int(value) if value is not None else None

    @property
    def distance(self):
        return self._distance
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @distance.setter
    def distance(self, value):
        self._distance = int(value) if value is not None else None

    @property
    def discard(self):
        return self._discard
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @discard.setter
    def discard(self, value):
        self._discard = bool(value) if value is not None else None
