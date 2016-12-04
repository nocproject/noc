# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IAuthenticationForn interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, ListOfParameter, DictParameter, StringParameter


class IAuthenticationForm(Interface):
    returns = ListOfParameter(element=DictParameter(attrs={
        "xtype": StringParameter(),
        "name": StringParameter()
    }))
