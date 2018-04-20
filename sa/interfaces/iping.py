# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (IPParameter, DictParameter,
                  IntParameter, BooleanParameter, StringParameter, FloatParameter)


class IPing(BaseInterface):
=======
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IPing(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    address = IPParameter()
    count = IntParameter(required=False)
    source_address = IPParameter(required=False)
    size = IntParameter(required=False)
    df = BooleanParameter(required=False)
    vrf = StringParameter(required=False)
    returns = DictParameter(attrs={
        "success": IntParameter(),
<<<<<<< HEAD
        "count": IntParameter(),
        "min": FloatParameter(required=False),
        "avg": FloatParameter(required=False),
        "max": FloatParameter(required=False)
=======
        "count": IntParameter()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    })
