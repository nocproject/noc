# -*- coding: utf-8 -*-
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
    changed_prefix_lists = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "prefix_list": ListOfParameter(element=IPv4PrefixParameter()),
        "strict": BooleanParameter()
    }))
    returns = ListOfParameter(element=DictParameter(attrs={
        "name": StringParameter(),
        "status": BooleanParameter()
    }))
