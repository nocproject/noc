# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetInventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import (DictListParameter, StringParameter, BooleanParameter, FloatParameter,
                  StringListParameter, REStringParameter)


class IGetInventory(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetInventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetInventory(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictListParameter(attrs={
        # Object type, used in ConnectionRule
        "type": StringParameter(required=False),
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
<<<<<<< HEAD
        #
        "mfg_date": REStringParameter(r"^\d{4}-\d{2}-\d{2}$",
                                      required=False),
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
    preview = "NOC.sa.managedobject.scripts.ShowInventory"
