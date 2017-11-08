# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# crm.supplier application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.crm.models.supplier import Supplier
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class SupplierApplication(ExtDocApplication):
    """
    Supplier application
    """
    title = _("Supplier")
    menu = [_("Setup"), _("Supplier")]
    model = Supplier
    query_fields = ["name__icontains"]

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile and o.profile.style else ""
