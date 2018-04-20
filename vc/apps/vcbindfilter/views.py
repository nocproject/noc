# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vcbindfilter application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.vc.models import VCBindFilter


class VCBindFilterApplication(ExtModelApplication):
    """
    VCBindFilter application
    """
    title = "VC Bind Filters"
    menu = "Setup | VC Bind Filters"
    model = VCBindFilter

    def field_vc_filter_expression(self, obj):
        """
        Build vc_filter_expression parameter
        :param obj:
        :return:
        """
        return obj.vc_filter.expression

