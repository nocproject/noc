# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetActivatorInfo
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from base import DictListParameter, StringParameter, IntParameter


class IGetActivatorInfo(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetActivatorInfo
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *


class IGetActivatorInfo(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = DictListParameter(attrs={
        "timestamp": IntParameter(),
        "pool": StringParameter(),
        "instance": StringParameter(),
        "state": StringParameter(),
        "last_state_change": IntParameter(),
        "max_scripts": IntParameter(),
        "current_scripts": IntParameter(),
        "scripts_processed": IntParameter(),
        "scripts_failed": IntParameter(),
        "scripts": DictListParameter(attrs={
            "script": StringParameter(),
            "object_name": StringParameter(),
            "address": StringParameter(),
            "start_time": IntParameter(),
            "timeout": IntParameter()
        })
    })
