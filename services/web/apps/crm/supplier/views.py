# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# crm.supplier application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.lib.app.decorators.state import state_handler
from noc.crm.models.supplier import Supplier
from noc.core.translation import ugettext as _


@state_handler
class SupplierApplication(ExtDocApplication):
    """
    Supplier application
    """
    title = _("Supplier")
    menu = [_("Setup"), _("Supplier")]
    model = Supplier
    query_fields = ["name__icontains"]

    def field_row_class(self, o):
        if o.profile and o.profile.style:
            return o.profile.style.css_class_name
        return ""
