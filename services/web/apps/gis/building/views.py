# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# gis.building application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.gis.models.address import Address
from noc.gis.models.building import Building
from noc.gis.models.division import Division
from noc.lib.app.docinline import DocInline
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class AddressInline(DocInline):
    def field_text_address(self, o):
        return o.display_ru()


class BuildingApplication(ExtDocApplication):
    """
    Building application
    """
    title = _("Building")
    menu = [_("Setup"), _("Buildings")]
    glyph = "building"
    model = Building
    parent_model = Division
    parent_field = "parent"
    default_ordering = ["sort_order"]
    query_fields = ["sort_order__icontains"]

    addresses = AddressInline(Address)

    def field_full_path(self, o):
        a = o.primary_address
        if not a:
            return o.adm_division.full_path
        return a.display_ru(levels=10)
