# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetObjectStatus interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import (Interface, ListOfParameter, DictParameter,
                  StringParameter, BooleanParameter)


class IGetObjectStatus(Interface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "status": BooleanParameter()
    }))
    preview = "NOC.sa.managedobject.scripts.ShowObjectStatus"
