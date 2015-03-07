# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Local user
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class User(BaseFact):
    ATTRS = ["name", "level", "[groups]"]

    def __init__(self, name=None, level=None, groups=None):
        self.name = name
        self.level = level
        self.groups = groups

    def __unicode__(self):
        return "User %s" % self.name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value or None
        
    @property
    def level(self):
        return self._level
    
    @level.setter
    def level(self, value):
        self._level = value

    @property
    def groups(self):
        return self._groups
    
    @groups.setter
    def groups(self, value):
        self._groups = value or []
