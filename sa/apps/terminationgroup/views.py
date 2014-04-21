# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.terminationgroup application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import TerminationGroup


class TerminationGroupApplication(ExtModelApplication):
    """
    TerminationGroup application
    """
    title = "Termination Group"
    menu = "Setup | Termination Groups"
    model = TerminationGroup
    query_fields = ["name__icontains"]