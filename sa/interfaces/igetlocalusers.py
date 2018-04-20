# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# IGetUsers interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import ListOfParameter, DictParameter, StringParameter, BooleanParameter


#
# Commonly accepted classes are:
# superuser, operator
#
#
class IGetLocalUsers(BaseInterface):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    returns = ListOfParameter(element=DictParameter(attrs={
        "username": StringParameter(),
        "class": StringParameter(),
        "is_active": BooleanParameter(default=True)
        }))
    preview = "NOC.sa.managedobject.scripts.ShowLocalUsers"
