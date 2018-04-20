# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# VRF fact
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## VRF fact
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from base import BaseFact


class VRF(BaseFact):
    ATTRS = ["name", "rd"]
    ID = ["name", "rd"]

    def __init__(self, name, rd=None):
        super(VRF, self).__init__()
        self.name = name
        self.rd = rd

    def __unicode__(self):
        return "VRF %s" % self.name

    @property
    def name(self):
        return self._name
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @name.setter
    def name(self, value):
        self._name = value or None

    @property
    def rd(self):
        return self._rd
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @rd.setter
    def rd(self, value):
        self._rd = value or None
