# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Inventory module datasources
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.datasource import DataSource
from noc.inv.models import *


class InterfaceDS(DataSource):
    _name = "inv.InterfaceDS"

    def __init__(self, managed_object, interface):
        self._interface = Interface.objects.filter(
            managed_object=managed_object.id,
            name=managed_object.profile.convert_interface_name(interface)
        ).first()

    @property
    def description(self):
        if not self._interface:
            return None
        return self._interface.description
