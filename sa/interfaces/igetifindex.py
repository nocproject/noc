# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetIfIndex - Get ifIndex by interface name
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import Interface, InterfaceNameParameter, IntParameter, NoneParameter


class IGetIfIndex(Interface):
    interface = InterfaceNameParameter()
    returns = IntParameter() | NoneParameter()
