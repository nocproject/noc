# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# VLAN
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## VLAN
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @id.setter
    def id(self, value):
        if value:
            value = int(value)
        self._id = value or None

    @property
    def name(self):
        return self._name
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @name.setter
    def name(self, value):
        self._name = value or None
