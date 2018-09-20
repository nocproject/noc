# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Invetory Collector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseCollector
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.subinterface import SubInterface


class InventoryObjectCollector(BaseCollector):
    name = "inventory"

    def iter_metrics(self):

        # @todo by POOL / Adm Domain
        yield ("inventory_iface_count"), Interface.objects.filter().count()
        yield ("inventory_iface_physical_count"), Interface.objects.filter(type="physical").count()
        yield ("inventory_link_count"), Link.objects.filter().count()
        yield ("inventory_subinterface_count"), SubInterface.objects.filter().count()
