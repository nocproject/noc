# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Inventory module datasources
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.datasource import DataSource
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface


class InterfaceDS(DataSource):
    _name = "inv.InterfaceDS"

    def __init__(self, managed_object, interface=None, ifindex=None):
        if not interface and not ifindex:
            self._interface = None
            return
        q = {
            "managed_object": managed_object.id
        }
        if interface:
            q["name"] = managed_object.profile.convert_interface_name(interface)
        if ifindex:
            q["ifindex"] = int(ifindex)
        self._description = None
        self._interface = Interface.objects.filter(**q).first()
        if self._interface:
            self._description = self._interface.description
        else:
            # Try to find subinterface
            si = SubInterface.objects.filter(**q).first()
            if si:
                self._description = si.description
                self._interface = si.interface

    @property
    def name(self):
        if not self._interface:
            return None
        return self._interface.name

    @property
    def description(self):
        return self._description

    @property
    def link(self):
        if not self._interface:
            return None
        link = self._interface.link
        if link:
            return str(link.id)
        else:
            return None
