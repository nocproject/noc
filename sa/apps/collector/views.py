# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.collector application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import Collector


class CollectorApplication(ExtModelApplication):
    """
    Collector application
    """
    title = "Collector"
    menu = "Setup | Collectors"
    model = Collector
