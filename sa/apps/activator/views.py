# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.activator application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models.activator import Activator


class ActivatorApplication(ExtModelApplication):
    """
    Activator application
    """
    title = "Activator"
    menu = "Setup | Activators"
    model = Activator
