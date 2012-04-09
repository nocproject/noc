# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetChassisID
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *


class IGetChassisID(Interface):
    returns = MACAddressParameter()
    template = "interfaces/igetchassisid.html"
