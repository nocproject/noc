# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
# NOC modules
=======
##----------------------------------------------------------------------
## Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from base import BaseFact
from noc.inv.models.interface import Interface as DBInterface

logger = logging.getLogger(__name__)


class Interface(BaseFact):
    ATTRS = ["name", "description", "admin_status", "speed", "duplex",
             "[protocols]", "profile", "type", "mac", "default_name",
             "aggregated_interface"]
    ID = ["name"]

    def __init__(self, name, description=None, admin_status=False, 
                 speed="auto", duplex="auto", protocols=None,
                 profile=None, type=None, mac=None, default_name=None,
                 aggregated_interface=None,
                 **kwargs):
        super(Interface, self).__init__()
        self.name = name
        self.description = description
        self.admin_status = admin_status
        self.has_description = False
        self.speed = speed
        self.duplex = duplex
        self.protocols = protocols
        self.profile = profile
        self.type = type
        self.mac = mac
        self.default_name = default_name
        self.aggregated_interface = aggregated_interface

    def __unicode__(self):
        return "Interface %s" % self.name
<<<<<<< HEAD

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

=======
        
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
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @has_description.setter
    def has_description(self, value):
        pass

    @property
    def speed(self):
        return self._speed
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @speed.setter
    def speed(self, value):
        self._speed = value or "auto"

    @property
    def duplex(self):
        return self._duplex
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, value):
        self._mac = value

    @property
    def default_name(self):
        return self._default_name or self.name

    @default_name.setter
    def default_name(self, value):
        self._default_name = value
        if not self.name:
            self.name = value

    @property
    def aggregated_interface(self):
        return self._aggregated_interface

    @aggregated_interface.setter
    def aggregated_interface(self, value):
        self._aggregated_interface = value or None

    def bind(self):
        if self.name:
<<<<<<< HEAD
            self.name = self.managed_object.get_profile().convert_interface_name(self.name)
=======
            self.name = self.managed_object.profile.convert_interface_name(self.name)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            iface = DBInterface.objects.filter(
                managed_object=self.managed_object.id,
                name=self.name
            ).first()
            if iface:
                logger.debug("bind %s to database", unicode(self))
                if iface.profile:
                    self.profile = iface.profile.name
            if not self.type:
<<<<<<< HEAD
                self.type = self.managed_object.get_profile().get_interface_type(self.name)
=======
                self.type = self.managed_object.profile.get_interface_type(self.name)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
