# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Fix PoP links
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.inv.util.pop_links import LinkedPoP


def fix():
    pop_models = ObjectModel.objects.filter(name__startswith="PoP |").values_list("id")
    pops = Object.objects.filter(object_model__in=pop_models).values_list("id")
    for p in pops:
        lp = LinkedPoP(p)
        lp.update_links()
