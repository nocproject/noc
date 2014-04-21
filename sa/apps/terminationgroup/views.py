# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.terminationgroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.lib.app.modelinline import ModelInline
from noc.sa.models.terminationgroup import TerminationGroup
from noc.ip.models.ippool import IPPool


class TerminationGroupApplication(ExtModelApplication):
    """
    TerminationGroup application
    """
    title = "Termination Group"
    menu = "Setup | Termination Groups"
    model = TerminationGroup
    query_fields = ["name__icontains"]
    ippool = ModelInline(IPPool)
