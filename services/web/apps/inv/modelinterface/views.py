# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.modelinterface application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.modelinterface import ModelInterface


class ModelInterfaceApplication(ExtDocApplication):
    """
    ModelInterface application
    """
    title = "Model Interface"
    menu = "Setup | Model Interfaces"
    model = ModelInterface
    query_fields = ["name__icontains", "description__icontains"]

    def cleaned_query(self, q):
        if "label" in q:
            q["name"] = q["label"]
            del q["label"]
        return super(ModelInterfaceApplication, self).cleaned_query(q)
