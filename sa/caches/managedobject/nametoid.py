## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MO name -> id cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from noc.core.cache.base import BaseCache
from noc.sa.models.managedobject import ManagedObject


class MONameToIdCache(BaseCache):
    """
    Resolve object's id by name
    """
    name = "sa.managedobject.nametoid"

    def __missing__(self, item):
        r = ManagedObject.objects.filter(name=item).values_list("id")
        if r:
            return r[0][0]
        else:
            raise KeyError(item)


mo_name_to_id = MONameToIdCache()
