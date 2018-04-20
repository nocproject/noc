# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Local user
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Local user
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from base import BaseFact


class User(BaseFact):
    ATTRS = ["name", "level", "[groups]"]
    ID = ["name"]

    def __init__(self, name=None, level=None, groups=None):
        super(User, self).__init__()
        self.name = name
        self.level = level
        self.groups = groups

    def __unicode__(self):
        return "User %s" % self.name

    @property
    def name(self):
        return self._name
<<<<<<< HEAD

    @name.setter
    def name(self, value):
        self._name = value or None

    @property
    def level(self):
        return self._level

=======
    
    @name.setter
    def name(self, value):
        self._name = value or None
        
    @property
    def level(self):
        return self._level
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @level.setter
    def level(self, value):
        self._level = value

    @property
    def groups(self):
        return self._groups
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @groups.setter
    def groups(self, value):
        self._groups = value or []
