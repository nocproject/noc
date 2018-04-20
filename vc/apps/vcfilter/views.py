# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vc.vcfilter application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.vc.models import VCFilter
from noc.sa.interfaces import IntParameter


class VCFilterApplication(ExtModelApplication):
    """
    VCFilter application
    """
    title = "VC Filter"
    menu = "Setup | VC Filters"
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
