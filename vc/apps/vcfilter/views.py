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


class VCFilterApplication(ExtModelApplication):
    """
    VCFilter application
    """
    title = "VC Filter"
    menu = "Setup | VC Filters"
    model = VCFilter
