# -*- coding: utf-8 -*-
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
    objects = ListOfParameter(element=IntParameter(), required=False)
    returns = ListOfParameter(element=DictParameter(attrs={
        "object_id": IntParameter(),
        "status": BooleanParameter() | NoneParameter()  # Up/Down/Unknown
    }))
    template = "interfaces/igetobjectsstatus.html"
