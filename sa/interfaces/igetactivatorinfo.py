# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetActivatorInfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetActivatorInfo(Interface):
    returns = DictListParameter(attrs={
        "timestamp": IntParameter(),
        "pool": StringParameter(),
        "instance": StringParameter(),
        "state": StringParameter(),
        "last_state_change": IntParameter(),
        "max_scripts": IntParameter(),
        "current_scripts": IntParameter(),
        "scripts_processed": IntParameter(),
        "scripts": DictListParameter(attrs={
            "script": StringParameter(),
            "address": StringParameter(),
            "start_time": IntParameter(),
            "timeout": IntParameter()
        })
    })
