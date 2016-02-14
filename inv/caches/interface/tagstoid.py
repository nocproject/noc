## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Influx tags to interface id
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from noc.core.cache.base import BaseCache
from noc.inv.models.interface import Interface
from noc.sa.caches.managedobject.nametoid import mo_name_to_id



class InterfaceTagsToIdCache(BaseCache):
    """
    Resolve interface if by influxdb tags
    key: {object: <name>, interface: <name>}
    """
    name = "inv.interface.tagstoid"

    def __missing__(self, item):
        if "object" not in item and "interface" not in item:
            raise KeyError(item)
        mo = mo_name_to_id[item["object"]]
        i = Interface._get_collection().find_one({
            "managed_object": mo,
            "name": item["interface"]
        })
        if i:
            return i["_id"]
        else:
            raise KeyError(item)


interface_tags_to_id = InterfaceTagsToIdCache()
