# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetUsers interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

##
## Commonly accepted classes are:
## superuser, operator
## 
##
class IGetLocalUsers(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
        "username" : StringParameter(),
        "class"    : StringParameter(),
        "is_active": BooleanParameter(default=True),
        }))
