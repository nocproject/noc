# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetObjectStatus interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  StringParameter, BooleanParameter)


class IGetObjectStatus(BaseInterface):
=======
##----------------------------------------------------------------------
## IGetObjectStatus interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetObjectStatus(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "status": BooleanParameter()
    }))
    preview = "NOC.sa.managedobject.scripts.ShowObjectStatus"
