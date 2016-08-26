# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Set Object paths
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.objectpath import ObjectPath


def fix():
    for mo in ManagedObject.objects.all():
        ObjectPath.refresh(mo)
