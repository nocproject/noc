# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Inventory module datasources
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.datasource import DataSource
from noc.inv.models import *


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
        self._interface = Interface.objects.filter(**q).first()

    @property
    def name(self):
        if not self._interface:
            return None
        return self._interface.name

    @property
    def description(self):
        if not self._interface:
            return None
        return self._interface.description

    @property
    def link(self):
        if not self._interface:
            return None
        link = self._interface.link
        if link:
            return str(link.id)
        else:
            return None
