# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.building application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.lib.app.docinline import DocInline
from noc.gis.models.building import Building
from noc.gis.models.address import Address


class AddressInline(DocInline):
    def field_text_address(self, o):
        return o.display_ru()


class BuildingApplication(ExtDocApplication):
    """
    Building application
    """
    title = "Building"
    menu = "Setup | Buildings"
    model = Building

    addresses = AddressInline(Address)

    def field_full_path(self, o):
        a = o.primary_address
        if not a:
            return o.adm_division.full_path
        return a.display_ru(levels=10)
