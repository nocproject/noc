# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetObjectsStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  IntParameter, BooleanParameter, NoneParameter)


class IGetObjectsStatus(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetObjectsStatus interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetObjectsStatus(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    objects = ListOfParameter(element=IntParameter(), required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "object_id": IntParameter(),
        "status": BooleanParameter() | NoneParameter()  # Up/Down/Unknown
    }))
