# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetInventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetInventory(Interface):
    returns = DictParameter(attrs={
        # List of objects found
        "objects": DictListParameter(attrs={
            # Unique internal id
            # May be changed during script runs
            # Used only as reference in connections
            "id": IntParameter(),
            # List of part numbers
            # May contain
            # * NOC model name
            # * asset.part_no* value (Part numbers)
            # * asset.order_part_no* value (FRU numbers)
            "part_no": StringListParameter(),
            # Optional revision
            "revision": StringParameter(required=False),
            # Serial number
            "serial": StringParameter(required=False),
            # Optional description
            "description": StringParameter(required=False)
        }),
        # List of connections between objects
        "connections": DictListParameter(attrs={
            # value of object.id
            "object1": IntParameter(),
            # Connection name of object 1
            "name1": StringParameter(),
            # value of object.id
            "object2": IntParameter(),
            # Connection name of object 2
            "name2": StringParameter(),
            # ModelData
            "data": DictParameter(required=False)
        })
    })
