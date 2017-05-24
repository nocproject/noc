# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# vc.vcfilter application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.vc.models import VCFilter
from noc.sa.interfaces.base import IntParameter
from noc.core.translation import ugettext as _


class VCFilterApplication(ExtModelApplication):
    """
    VCFilter application
    """
    title = _("VC Filter")
    menu = [_("Setup"), _("VC Filters")]
    model = VCFilter

    def lookup_vc(self, q, name, value):
        """
        Resolve __vc lookups
        :param q:
        :param name:
        :param value:
        :return:
        """
        value = IntParameter().clean(value)
        filters = [str(f.id) for f in VCFilter.objects.all() if f.check(value)]
        if filters:
            x = "(id IN (%s))" % ", ".join(filters)
        else:
            x = "FALSE"
        try:
            q[None] += [x]
        except KeyError:
            q[None] = [x]
