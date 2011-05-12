# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.model application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011
## The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import TreeApplication
from noc.inv.models import Model, ModelCategory


class ModelApplication(TreeApplication):
    title = "Models"
    verbose_name = "Model"
    verbose_name_plural = "Models"
    menu = "Setup | Models"
    model = Model
    category_model = ModelCategory
