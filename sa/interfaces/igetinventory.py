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
    returns = DictListParameter(attrs={
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
        "description": StringParameter(required=False),
        #
        "connections": DictListParameter(attrs={
            # Local connection name, according to model
            "name": StringParameter(),
            # Remote object internal id
            # Must match with objects.id field
            "object": IntParameter(),
            # Remote connection name, according to model
            "remote_name": StringParameter(),
            # ModelData
            "data": DictParameter(required=False)
        }, required=False),
        # Optional internal crossing
        "crossing": DictListParameter(attrs={
            # Input connection name, according to model
            "in": StringParameter(),
            # Output connection name, according to model
            "out": StringParameter(),
            # Power gain, in dB
            "gain": FloatParameter()
        }, required=False)
    })
