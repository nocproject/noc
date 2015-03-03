# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class Interface(BaseFact):
    ATTRS = ["name", "description", "admin_status", "speed", "duplex"]

    def __init__(self, name, description=None, admin_status=False, 
                 speed="auto", duplex="auto"):
        self.name = name
        self.description = description
        self.admin_status = admin_status
        self.has_description = False
        self.speed = speed
        self.duplex = duplex

    def __unicode__(self):
        return u"interface %s" % self.name
        
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value or None
        
    @property
    def admin_status(self):
        return self._admin_status
    
    @admin_status.setter
    def admin_status(self, value):
        self._admin_status = bool(value)
        
    @property
    def has_description(self):
        return bool(self._description)
    
    @has_description.setter
    def has_description(self, value):
        pass

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, value):
        self._speed = value or "auto"

    @property
    def duplex(self):
        return self._duplex
    
    @duplex.setter
    def duplex(self, value):
        if value:
            value = str(value).lower()
            if value.startswith("full"):
                value = "full"
            elif value.startswith("half"):
                value = "half"
        self._duplex = value or "auto"
