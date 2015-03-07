# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from base import BaseFact
from noc.inv.models.interface import Interface as DBInterface

logger = logging.getLogger(__name__)


class Interface(BaseFact):
    ATTRS = ["name", "description", "admin_status", "speed", "duplex",
             "[protocols]", "profile", "type"]

    def __init__(self, name, description=None, admin_status=False, 
                 speed="auto", duplex="auto", protocols=None):
        super(Interface, self).__init__()
        self.name = name
        self.description = description
        self.admin_status = admin_status
        self.has_description = False
        self.speed = speed
        self.duplex = duplex
        self.protocols = protocols
        self.profile = None
        self.type = None

    def __unicode__(self):
        return "Interface %s" % self.name
        
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

    @property
    def protocols(self):
        return self._protocols

    @protocols.setter
    def protocols(self, value):
        self._protocols = value or []

    def add_protocol(self, protocol):
        if protocol not in self.protocols:
            self.protocols += [protocol]

    def remove_protocol(self, protocol):
        if protocol in self.protocols:
            self.protocols.remove(protocol)

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    def bind(self):
        if self.name:
            self.name = self.managed_object.profile.convert_interface_name(self.name)
            iface = DBInterface.objects.filter(
                managed_object=self.managed_object.id,
                name=self.name
            ).first()
            if iface:
                logger.debug("bind %s to database", unicode(self))
                if iface.profile:
                    self.profile = iface.profile.name
            if not self.type:
                self.type = self.managed_object.profile.get_interface_type(self.name)
