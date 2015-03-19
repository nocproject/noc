# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VLAN
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class VLAN(BaseFact):
    ATTRS = ["id", "name"]
    ID = ["id"]

    def __init__(self, id, name=None):
        super(VLAN, self).__init__()
        self.id = id
        self.name = name

    def __unicode__(self):
        r = "VLAN %d" % self.id
        if self.name and self.name != str(self.id):
            r += " (%s)" % self.name
        return r

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        if value:
            value = int(value)
        self._id = value or None

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value or None
