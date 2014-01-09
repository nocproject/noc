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
        # Object type, used in ConnectionRule
        "type": StringParameter(),
        # Object number as reported by script
        "number": StringParameter(required=False),
        # Builtin modules apply ConnectionRule scopes
        # But does not submitted into database
        "builtin": BooleanParameter(default=False),
        # Object vendor. Must match Vendor.code
        "vendor": StringParameter(),
        # List of part numbers
        # May contain
        # * NOC model name
        # * asset.part_no* value (Part numbers)
        # * asset.order_part_no* value (FRU numbers)
        "part_no": StringListParameter(convert=True),
        # Optional revision
        "revision": StringParameter(required=False),
        # Serial number
        "serial": StringParameter(required=False),
        # Optional description
        "description": StringParameter(required=False),
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
