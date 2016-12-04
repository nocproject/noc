# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetUptime
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Interface, FloatParameter, NoneParameter


class IGetUptime(Interface):
    """
    System uptime in seconds
    """
    returns = NoneParameter() | FloatParameter()
