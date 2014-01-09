# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.modelmapping application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models import ModelMapping


class ModelMappingApplication(ExtDocApplication):
    """
    ModelMapping application
    """
    title = "Model Mapping"
    menu = "Setup | Model Mapping"
    model = ModelMapping
