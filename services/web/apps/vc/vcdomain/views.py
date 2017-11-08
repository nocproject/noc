# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# vc.vcdomain application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.vc.models import VCDomain


class VCDomainApplication(ExtModelApplication):
    """
    VCDomain application
    """
    title = _("VC Domain")
    menu = [_("Setup"), _("VC Domains")]
    model = VCDomain
    query_fields = ["name", "description"]
    query_condition = "icontains"

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""

    def field_object_count(self, o):
        return o.managedobject_set.count()
