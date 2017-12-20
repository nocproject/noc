# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# vc.vcbindfilter application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.vc.models.vcbindfilter import VCBindFilter
from noc.core.translation import ugettext as _


class VCBindFilterApplication(ExtModelApplication):
    """
    VCBindFilter application
    """
    title = _("VC Bind Filters")
    menu = [_("Setup"), _("VC Bind Filters")]
    model = VCBindFilter

    def field_vc_filter_expression(self, obj):
        """
        Build vc_filter_expression parameter
        :param obj:
        :return:
        """
        return obj.vc_filter.expression
