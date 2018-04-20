# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# ISyncPrefixLists interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.interface.base import BaseInterface
from base import (ListOfParameter, DictParameter,
                  StringParameter, BooleanParameter, IPv4PrefixParameter)


class ISyncPrefixLists(BaseInterface):
=======
##----------------------------------------------------------------------
## ISyncPrefixLists interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class ISyncPrefixLists(Interface):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    changed_prefix_lists = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "prefix_list": ListOfParameter(element=IPv4PrefixParameter()),
        "strict": BooleanParameter()
    }))
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "status": BooleanParameter()
    }))
